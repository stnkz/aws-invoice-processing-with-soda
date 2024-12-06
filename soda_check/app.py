import logging
import os

from soda.scan import Scan

logger = logging.getLogger()
logger.setLevel("INFO")

HOST = os.getenv("POSTGRES_EC2_INSTANCE_HOST")
USER = os.getenv("POSTGRES_EC2_INSTANCE_USER")
PASSWORD = os.getenv("POSTGRES_EC2_INSTANCE_PASSWORD")
DATABASE = os.getenv("POSTGRES_EC2_INSTANCE_DATABASE")


def lambda_handler(event, context):
    scan = Scan()
    # Specifies which datasource to use for the checks.
    scan.set_data_source_name("invoices")
    # Adds configurations from a YAML formatted string.
    scan.add_configuration_yaml_str(
        f"""
        data_source invoices:
            type: postgres
            connection:
            host: {HOST}
            username: {USER}
            password: {PASSWORD}
            database: {DATABASE}
            schema: public
    """
    )

    checks = """
    checks for invoices:
        # Numeric metrics
        - row_count > 0
        - duplicate_count(invoice_key) = 0
        - max(amount) <= 10000
        - max_length(invoice_desc) < 400
        - min(amount) >= 1
        - percentile(amount, 0.95) > 50
        # Missing metrics
        - missing_count(amount) = 0
        # Schema checks
        - schema:
            name: Confirm that required columns are present
            fail:
                when required column missing:
                - invoice_key 
                - amount
        # Check for valid values
        - invalid_count(invoice_key) = 0:
            valid min length: 2
        - invalid_count(name) = 0:
            valid min length: 2
     """

    # Add a SodaCL YAML string to the scan.
    scan.add_sodacl_yaml_str(checks)

    # Set logs to verbose mode, equivalent to CLI -V option
    scan.set_verbose(True)

    # Execute the scan
    exit_code = scan.execute()

    # Inspect the scan result
    scan_results = scan.get_scan_results()
    logger.info(f"scan_results: {scan_results}")

    # Inspect the scan logs
    logs_text = scan.get_logs_text()
    logger.info(f"logs_text: {logs_text}")

    # Advanced methods to inspect scan execution logs
    if scan.has_error_logs():
        logger.info(f"error_logs_text: {scan.get_error_logs_text()}")

    # Advanced methods to review check results details
    if scan.has_check_fails():
        logger.info(f"checks_fail: {scan.get_checks_fail()}")
        logger.info(f"checks_fail_text: {scan.get_checks_fail_text()}")

    if scan.has_checks_warn_or_fail():
        logger.info(f"checks_warn_or_fail: {scan.get_checks_warn_or_fail()}")
        logger.info(f"checks_warn_or_fail_text: {scan.get_checks_warn_or_fail_text()}")

    logger.info(f"all_checks_text(): {scan.get_all_checks_text()}")

    # Assert options
    scan.assert_no_error_logs()
    scan.assert_no_checks_fail()
    scan.assert_no_checks_warn_or_fail()
    assert exit_code == 0

    return event


if __name__ == "__main__":
    lambda_handler(None, None)
