# scm_config_clone/commands/security/security_rule.py

import logging
from typing import List, Optional, Any, Dict

import typer
from scm.client import Scm
from scm.config.security import SecurityRule
from scm.exceptions import (
    AuthenticationError,
    InvalidObjectError,
    MissingQueryParameterError,
    NameNotUniqueError,
    ObjectNotPresentError,
)
from scm.models.security import SecurityRuleCreateModel, SecurityRuleResponseModel
from tabulate import tabulate

from scm_config_clone.utilities import (
    compare_object_lists,
    load_settings,
    parse_csv_option,
)


def build_create_params(
    src_obj: SecurityRuleResponseModel,
    destination: str,
    context_type: str = "folder",
) -> Dict[str, Any]:
    """
    Construct the dictionary of parameters required to create a new security rule.

    Given an existing SecurityRuleResponseModel (source object), a destination folder or snippet,
    and an optional context type, this function builds a dictionary with all necessary fields for creating
    a new security rule in the destination tenant. It uses `model_dump` on a Pydantic model
    to ensure only valid, explicitly set fields are included.

    Args:
        src_obj: The SecurityRuleResponseModel representing the source security rule.
        destination: The folder or snippet in the destination tenant where the object should be created.
        context_type: The type of destination context (folder/snippet). Defaults to "folder".

    Returns:
        A dictionary containing the fields required for `SecurityRule.create()`.
        This dictionary is validated and pruned by SecurityRuleCreateModel.
    """
    data = {
        "name": src_obj.name,
        context_type: destination,
        "description": src_obj.description if src_obj.description is not None else None,
        "tag": src_obj.tag if src_obj.tag else [],
        "from_": src_obj.from_,
        "source": src_obj.source,
        "negate_source": src_obj.negate_source,
        "source_user": src_obj.source_user,
        "source_hip": src_obj.source_hip,
        "to_": src_obj.to_,
        "destination": src_obj.destination,
        "negate_destination": src_obj.negate_destination,
        "destination_hip": src_obj.destination_hip,
        "application": src_obj.application,
        "service": src_obj.service,
        "category": src_obj.category,
        "action": src_obj.action,
        "profile_setting": src_obj.profile_setting,
        "log_setting": src_obj.log_setting,
        "schedule": src_obj.schedule,
        "log_start": src_obj.log_start,
        "log_end": src_obj.log_end,
        "disabled": src_obj.disabled,
    }

    create_model = SecurityRuleCreateModel(**data)
    return create_model.model_dump(
        exclude_unset=True,
        exclude_none=True,
        by_alias=True,
    )


def security_rules(
    context_type: str = typer.Option(
        "folder",
        "--context",
        help="Specify the context type: 'folder' or 'snippet'",
    ),
    context_source_name: Optional[str] = typer.Option(
        None,
        "--source",
        help="Name of the source folder or snippet to retrieve objects from.",
    ),
    context_destination_name: Optional[str] = typer.Option(
        None,
        "--destination",
        help="Name of the destination folder or snippet to create objects in.",
    ),
    # Legacy parameters (deprecated)
    source_folder: Optional[str] = typer.Option(
        None,
        "--source-folder",
        help="[DEPRECATED] Use --source with --context=folder instead.",
    ),
    destination_folder: Optional[str] = typer.Option(
        None,
        "--destination-folder",
        help="[DEPRECATED] Use --destination with --context=folder instead.",
    ),
    rulebase: str = typer.Option(
        "pre",
        "--rulebase",
        help="The rulebase to target (pre or post).",
    ),
    exclude_folders: str = typer.Option(
        None,
        "--exclude-folders",
        help="Comma-separated list of folders to exclude from the retrieval.",
    ),
    exclude_snippets: str = typer.Option(
        None,
        "--exclude-snippets",
        help="Comma-separated list of snippets to exclude from the retrieval.",
    ),
    exclude_devices: str = typer.Option(
        None,
        "--exclude-devices",
        help="Comma-separated list of devices to exclude from the retrieval.",
    ),
    commit_and_push: bool = typer.Option(
        False,
        "--commit-and-push",
        help="If set, commit the changes on the destination tenant after object creation.",
        is_flag=True,
    ),
    auto_approve: bool = typer.Option(
        None,
        "--auto-approve",
        "-A",
        help="If set, skip the confirmation prompt and automatically proceed with creation.",
        is_flag=True,
    ),
    create_report: bool = typer.Option(
        None,
        "--create-report",
        "-R",
        help="If set, create or append to a 'result.csv' file with the task results.",
        is_flag=True,
    ),
    dry_run: bool = typer.Option(
        None,
        "--dry-run",
        "-D",
        help="If set, perform a dry run without applying any changes.",
        is_flag=True,
    ),
    quiet_mode: bool = typer.Option(
        None,
        "--quiet-mode",
        "-Q",
        help="If set, hide all console output (except log messages).",
        is_flag=True,
    ),
    logging_level: str = typer.Option(
        None,
        "--logging-level",
        "-L",
        help="Override the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
    ),
    settings_file: str = typer.Option(
        "settings.yaml",
        "--settings-file",
        "-s",
        help="Path to the YAML settings file containing tenant credentials and configuration.",
    ),
):
    """
    Clone security rules from a source SCM tenant to a destination SCM tenant.

    This Typer CLI command automates the process of retrieving security rules
    from a specified folder or snippet in a source tenant, optionally filters them out based
    on user-defined exclusion criteria, and then creates them in a destination tenant.

    The workflow is:
    1. Load authentication and configuration settings (e.g., credentials, logging) from the YAML file.
    2. If any runtime flags are provided, they override the corresponding settings from the file.
    3. Authenticate to the source tenant and retrieve security rules from the given folder or snippet.
    4. Display the retrieved source objects. If not auto-approved, prompt the user before proceeding.
    5. Authenticate to the destination tenant and create the retrieved objects there.
    6. If `--commit-and-push` is provided and objects were created successfully, commit the changes.
    7. Display the results, including successfully created objects and any errors.

    Args:
        context_type: Specify the context type ('folder' or 'snippet') for operations.
        context_source_name: Name of source folder or snippet to retrieve objects from.
        context_destination_name: Name of destination folder or snippet to create objects in.
        source_folder: [DEPRECATED] The source folder from which to retrieve security rules.
        destination_folder: [DEPRECATED] The destination folder from which to push security rules.
        rulebase: The rulebase to target (pre or post).
        exclude_folders: Comma-separated folder names to exclude from source retrieval.
        exclude_snippets: Comma-separated snippet names to exclude from source retrieval.
        exclude_devices: Comma-separated device names to exclude from source retrieval.
        commit_and_push: If True, commit changes in the destination tenant after creation.
        auto_approve: If True or set in settings, skip the confirmation prompt before creating objects.
        create_report: If True or set in settings, create/append a CSV file with task results.
        dry_run: If True or set in settings, perform a dry run without applying changes (logic TBD).
        quiet_mode: If True or set in settings, hide console output except log messages (logic TBD).
        logging_level: If provided, override the logging level from settings.yaml.
        settings_file: Path to the YAML settings file for loading authentication and configuration.

    Raises:
        typer.Exit: Exits if authentication fails, retrieval fails, or if the user opts not to proceed.
    """
    typer.echo("🚀 Starting security rule cloning...")

    # Load settings from file
    settings = load_settings(settings_file)

    # Apply fallback logic: if a flag wasn't provided at runtime, use settings.yaml values
    auto_approve = settings["auto_approve"] if auto_approve is None else auto_approve
    create_report = (
        settings["create_report"] if create_report is None else create_report
    )
    dry_run = settings["dry_run"] if dry_run is None else dry_run
    quiet_mode = settings["quiet"] if quiet_mode is None else quiet_mode

    # Logging level fallback
    if logging_level is None:
        logging_level = settings["logging"]
    logging_level = logging_level.upper()

    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, logging_level, logging.INFO))

    # Parse CSV options
    exclude_folders_list = parse_csv_option(exclude_folders)
    exclude_snippets_list = parse_csv_option(exclude_snippets)
    exclude_devices_list = parse_csv_option(exclude_devices)

    # Resolve parameters (prioritize new over legacy)
    resolved_source = context_source_name or source_folder
    resolved_destination = context_destination_name or destination_folder

    # Prompt if still None after resolution
    if resolved_source is None:
        resolved_source = typer.prompt(
            f"Name of source {context_type} where objects are located"
        )
    if resolved_destination is None:
        resolved_destination = typer.prompt(
            f"Name of destination {context_type} where objects will go"
        )

    # Authenticate with source
    try:
        source_creds = settings["source_scm"]
        source_client = Scm(
            client_id=source_creds["client_id"],
            client_secret=source_creds["client_secret"],
            tsg_id=source_creds["tenant"],
            log_level=logging_level,
        )
        logger.info(f"Authenticated with source SCM tenant: {source_creds['tenant']}")
    except (AuthenticationError, KeyError) as e:
        logger.error(f"Error authenticating with source tenant: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error with source authentication: {e}")
        raise typer.Exit(code=1)

    # Authenticate with destination
    try:
        destination_creds = settings["destination_scm"]
        destination_client = Scm(
            client_id=destination_creds["client_id"],
            client_secret=destination_creds["client_secret"],
            tsg_id=destination_creds["tenant"],
            log_level=logging_level,
        )
        logger.info(
            f"Authenticated with destination SCM tenant: {destination_creds['tenant']}"
        )
    except (AuthenticationError, KeyError) as e:
        logger.error(f"Error authenticating with destination tenant: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Unexpected error with destination authentication: {e}")
        raise typer.Exit(code=1)

    # Retrieve security rules from source
    try:
        source_rules_api = SecurityRule(source_client, max_limit=5000)

        # Call list() with different parameters based on context
        list_params = {
            "rulebase": rulebase,
            "exact_match": True,
            "exclude_folders": exclude_folders_list,
            "exclude_snippets": exclude_snippets_list,
            "exclude_devices": exclude_devices_list,
        }

        # Add context-specific parameter
        if context_type == "folder":
            list_params["folder"] = resolved_source
        else:  # context == "snippet"
            list_params["snippet"] = resolved_source

        source_objects = source_rules_api.list(**list_params)

        logger.info(
            f"Retrieved {len(source_objects)} security rules from source {context_type} '{resolved_source}'."
        )
    except Exception as e:
        logger.error(f"Error retrieving security rules from source: {e}")
        raise typer.Exit(code=1)

    # Retrieve security rules from destination
    try:
        destination_rules_api = SecurityRule(destination_client, max_limit=5000)

        # Different API call based on context type
        if context_type == "folder":
            destination_objects = destination_rules_api.list(
                folder=resolved_destination,
                rulebase=rulebase,
                exact_match=True,
                exclude_folders=exclude_folders_list,
                exclude_snippets=exclude_snippets_list,
                exclude_devices=exclude_devices_list,
            )
            logger.info(
                f"Retrieved {len(destination_objects)} rules from destination folder '{resolved_destination}'"
            )
        elif context_type == "snippet":
            # Check if the API supports retrieving by snippet directly
            destination_objects = destination_rules_api.list(
                snippet=resolved_destination,
                rulebase=rulebase,
                exact_match=True,
            )
            logger.info(
                f"Retrieved {len(destination_objects)} rules from destination snippet '{resolved_destination}'"
            )
        else:
            logger.error(f"Invalid context type: {context_type}")
            raise typer.Exit(code=1)
    except Exception as e:
        logger.error(f"Error retrieving rules: {e}")
        raise typer.Exit(code=1)

    # Compare and get the status information
    comparison_results = compare_object_lists(
        source_objects,
        destination_objects,
    )

    if source_objects and not quiet_mode:
        rule_table = []
        for result in comparison_results:
            # 'x' if already configured else ''
            status = "x" if result["already_configured"] else ""
            rule_table.append([result["name"], status])

        typer.echo(
            tabulate(
                rule_table,
                headers=["Name", "Destination Status"],
                tablefmt="fancy_grid",
            )
        )

    # Prompt if not auto-approved and objects exist
    if source_objects and not auto_approve:
        proceed = typer.confirm(
            "Do you want to proceed with creating these rules in the destination tenant?"
        )
        if not proceed:
            typer.echo("Aborting cloning operation.")
            raise typer.Exit(code=0)

    # Determine which objects need to be created (those not already configured)
    already_configured_names = {
        res["name"] for res in comparison_results if res["already_configured"]
    }

    objects_to_create = [
        obj for obj in source_objects if obj.name not in already_configured_names
    ]

    # Create security rules in destination
    destination_rules = SecurityRule(destination_client, max_limit=5000)
    created_objs: List[SecurityRuleResponseModel] = []
    error_objects: List[List[str]] = []

    for src_obj in objects_to_create:
        if dry_run:
            logger.info(
                f"Skipping creation of security rule in destination (dry run): {src_obj.name}"
            )
            continue

        if create_report:
            with open("result.csv", "a") as f:
                context_property = "folder" if context_type == "folder" else "snippet"
                f.write(
                    f"Security Rule,{src_obj.name},{getattr(src_obj, context_property)}\n"
                )

        try:
            create_params = build_create_params(
                src_obj=src_obj,
                destination=resolved_destination,
                context_type=context_type,
            )
        except ValueError as ve:
            error_objects.append([src_obj.name, str(ve)])
            continue

        try:
            new_obj = destination_rules.create(create_params, rulebase=rulebase)
            created_objs.append(new_obj)
            logger.info(f"Created security rule in destination: {new_obj.name}")
        except (
            InvalidObjectError,
            MissingQueryParameterError,
            NameNotUniqueError,
            ObjectNotPresentError,
        ) as e:
            if logging_level == "DEBUG":
                error_type = str(e)
            else:
                error_type = type(e).__name__
            error_objects.append([src_obj.name, error_type])
        except Exception as e:  # noqa
            if logging_level == "DEBUG":
                error_type = str(e)
            else:
                error_type = "Unknown Error, enable debug logging for more details."
            error_objects.append([src_obj.name, error_type])
            continue

    # Display results if not quiet_mode
    if created_objs and not quiet_mode:
        typer.echo("\nSuccessfully created the following security rules:")
        created_table = []
        for obj in created_objs:
            created_table.append([obj.name])

        typer.echo(
            tabulate(
                created_table,
                headers=["Name"],
                tablefmt="fancy_grid",
            )
        )

    if error_objects and not quiet_mode:
        typer.echo("\nSome security rules failed to be created:")
        typer.echo(
            tabulate(
                error_objects,
                headers=["Object Name", "Error"],
                tablefmt="fancy_grid",
            )
        )

    # Commit changes if requested and objects were created
    if commit_and_push and created_objs and context_type == "folder":
        try:
            commit_params = {
                "folders": [resolved_destination],
                "description": f"Cloned security rules from {context_type} {resolved_source}",
                "sync": True,
            }
            result = destination_rules.commit(**commit_params)
            job_status = destination_rules.get_job_status(result.job_id)
            logger.info(
                f"Commit job ID {result.job_id} status: {job_status.data[0].status_str}"
            )
        except Exception as e:
            logger.error(f"Error committing security rules in destination: {e}")
            raise typer.Exit(code=1)
    elif commit_and_push and created_objs and context_type == "snippet":
        logger.info(
            f"SCM does not support committing with a snippet context; perform this task on the destination tenant folder manually. Skipping commit."
        )
    else:
        if created_objs and not commit_and_push:
            logger.info(
                "Rules created, but --commit-and-push not specified, skipping commit."
            )
        else:
            logger.info("No new security rules were created, skipping commit.")

    typer.echo("🎉 Security rule cloning completed successfully! 🎉")
