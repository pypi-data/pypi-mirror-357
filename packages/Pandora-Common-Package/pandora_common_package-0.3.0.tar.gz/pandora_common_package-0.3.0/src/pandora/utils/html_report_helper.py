import argparse
import xml.etree.ElementTree as ET
from datetime import datetime
from html import escape
import re
import logging

# Configure module-level logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class HtmlReportHelper:
    class JunitToHtmlConverter:
        """
        This class aim to convert a junit xml report to html report,
        it should be used accompany by a specific html template.
        """

        @classmethod
        def _parse_junit_xml(cls, xml_path: str) -> dict:
            """
            (Protected method) Core function for parsing junit xml report,
            it will read xml report and load information to a dict variable.

            Args:
                xml_path (str):
                    The path of junit xml file (e.g: "./test-results.xml").

            Returns:
                dict:
                    Information of junit xml report with formatted html content,
                    specialize with _generate_html_report().
            """
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Get test suite information
            testsuite = root if root.tag == 'testsuite' else root.find('testsuite')

            suite_name = testsuite.get('name', 'Test Suite')
            total_tests = int(testsuite.get('tests', 0))
            failed_tests = int(testsuite.get('failures', 0))
            error_tests = int(testsuite.get('errors', 0))
            skipped_tests = int(testsuite.get('skipped', 0))
            passed_tests = total_tests - failed_tests - skipped_tests - error_tests
            total_time = float(testsuite.get('time', 0))

            # Extract all test cases
            testcases = []
            test_classes = {}
            failed_testcases = []
            error_testcases = []
            testcase_counter = 1

            for testcase in testsuite.findall('testcase'):
                classname = testcase.get('classname', 'UnknownClass')
                name = testcase.get('name', 'Unnamed Test')
                time_val = float(testcase.get('time', 0))

                # Generating unique ids
                test_id = f"testcase_{testcase_counter}"
                testcase_counter += 1

                # Checking test results
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')

                # Extract error messages and stack traces
                failure_message = ""
                failure_text = ""

                if failure is not None:
                    # Extract error messages (if exists)
                    failure_message = failure.get('message', '')

                    # Extract the error stack trace
                    if failure.text:
                        failure_text = failure.text.strip()
                    else:
                        # If failure.text is empty, try to get all the text content
                        failure_text = ''.join(failure.itertext()).strip()

                error_message = ""
                error_text = ""

                if error is not None:
                    # Extract error messages (if exists)
                    error_message = error.get('message', '')

                    # Extract the error stack trace
                    if error.text:
                        error_text = error.text.strip()
                    else:
                        # If failure.text is empty, try to get all the text content
                        error_text = ''.join(error.itertext()).strip()

                testcase_data = {
                    'id': test_id,
                    'classname': escape(classname),
                    'name': escape(name),
                    'time': round(time_val, 3),
                    'failed': failure is not None,
                    'error': error is not None,
                    'skipped': skipped is not None,
                    'failure_message': escape(failure_message),
                    'failure_text': escape(failure_text),
                    'error_message': escape(error_message),
                    'error_text': escape(error_text)
                }

                testcases.append(testcase_data)

                # Group by test class
                if classname not in test_classes:
                    test_classes[classname] = []
                test_classes[classname].append(testcase_data)

                # Log the failed test cases
                if failure is not None:
                    failed_testcases.append(testcase_data)
                if error is not None:
                    error_testcases.append(testcase_data)

            # Preparing template data
            template_data = {
                'suite_name': escape(suite_name),
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'error_tests': error_tests,
                'skipped_tests': skipped_tests,
                'total_time': round(total_time, 2),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Generating the directory section
            toc_classes = []
            for class_name, testcases_list in test_classes.items():
                testcase_items = []
                for testcase in testcases_list:
                    if testcase['failed']:
                        outcome_class = "outcome-failed"
                    elif testcase['error']:
                        outcome_class = "outcome-errors"
                    else:
                        outcome_class = ""
                    testcase_items.append(
                        f'<li class="{outcome_class}">'
                        f'<a href="#{testcase["id"]}">{testcase["name"]}</a>'
                        f'</li>'
                    )

                toc_classes.append(
                    f'<li>'
                    f'{escape(class_name)}'
                    f'<ul class="toc-list">{"".join(testcase_items)}</ul>'
                    f'</li>'
                )

            template_data['toc_classes'] = "\n".join(toc_classes)

            # Generate a list of failed tests
            failure_items = []
            for testcase in failed_testcases:
                failure_items.append(
                    f'<li class="outcome-failed">'
                    f'<a href="#{testcase["id"]}">{testcase["name"]}</a>'
                    f'</li>'
                )
            error_items = []
            for testcase in error_testcases:
                error_items.append(
                    f'<li class="outcome-errors">'
                    f'<a href="#{testcase["id"]}">{testcase["name"]}</a>'
                    f'</li>'
                )

            template_data['toc_failures'] = "\n".join(failure_items)
            template_data['toc_errors'] = "\n".join(error_items)

            # Generate the test case section
            test_classes_html = []
            for class_name, testcases_list in test_classes.items():
                testcases_html = []
                for testcase in testcases_list:
                    if testcase['failed']:
                        status_class = "failed"
                        status_text = "Failed"
                    elif testcase['error']:
                        status_class = "errors"
                        status_text = "Error"
                    elif testcase['skipped']:
                        status_class = "skipped"
                        status_text = "Skipped"
                    else:
                        status_class = "passed"
                        status_text = "Passed"

                    failure_html = ""
                    if testcase['failed']:
                        failure_html = (
                            f'<div class="testcase-content">'
                            f'<div class="testcase-failure">'
                            f'<div class="testcase-failure-title">Error Details</div>'
                            f'<p>{testcase["failure_message"]}</p>'
                            f'</div>'
                            f'<div class="testcase-error">'
                            f'<pre>{testcase["failure_text"]}</pre>'
                            f'</div>'
                            f'</div>'
                        )
                    if testcase['error']:
                        failure_html = (
                            f'<div class="testcase-content">'
                            f'<div class="testcase-error-content">'
                            f'<div class="testcase-error-title">Error Details</div>'
                            f'<p>{testcase["error_message"]}</p>'
                            f'</div>'
                            f'<div class="testcase-error">'
                            f'<pre>{testcase["error_text"]}</pre>'
                            f'</div>'
                            f'</div>'
                        )

                    testcases_html.append(
                        f'<div class="testcase-{status_class}" id="{testcase["id"]}">'
                        f'<div class="testcase-header">'
                        f'<div class="testcase-title">{testcase["name"]}</div>'
                        f'<table class="testcase-meta">'
                        f'<tr>'
                        f'<td class="status-{status_class}">'
                        f'<span class="testcase-status">Status: {status_text}</span>'
                        f'</td>'
                        f'<td class="testcase-duration">'
                        f'Duration: {testcase["time"]}s'
                        f'</td>'
                        f'</tr>'
                        f'</table>'
                        f'</div>'
                        f'{failure_html}'
                        f'</div>'
                    )

                test_classes_html.append(
                    f'<div class="testclass">'
                    f'<h4>{escape(class_name)}</h4>'
                    f'<div class="testcases">'
                    f'{"".join(testcases_html)}'
                    f'</div>'
                    f'</div>'
                )

            template_data['test_classes_html'] = "\n".join(test_classes_html)

            return template_data

        @classmethod
        def _generate_html_report(cls, template_path: str, report_data: dict, output_path: str):
            """
            (Protected method) Core function for generate html report,
            it should be used accompany by a specific html template and a dict source file from parse_junit_xml().

            Args:
                template_path (str):
                    The path of template html file (e.g: "./templates/email_report_template.html").
                report_data (dict):
                    Parsed dict data from parse_junit_xml().
                output_path (str):
                    The path of output html file (e.g: "./test-results-junit.html").
            """
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Replace variables in template
            report_html = template_content.replace('${suite_name}', report_data['suite_name'])
            report_html = report_html.replace('${total_tests}', str(report_data['total_tests']))
            report_html = report_html.replace('${passed_tests}', str(report_data['passed_tests']))
            report_html = report_html.replace('${failed_tests}', str(report_data['failed_tests']))
            report_html = report_html.replace('${error_tests}', str(report_data['error_tests']))
            report_html = report_html.replace('${skipped_tests}', str(report_data['skipped_tests']))
            report_html = report_html.replace('${total_time}', str(report_data['total_time']))
            report_html = report_html.replace('${timestamp}', report_data['timestamp'])
            report_html = report_html.replace('${toc_classes}', report_data['toc_classes'])
            report_html = report_html.replace('${toc_failures}', report_data['toc_failures'])
            report_html = report_html.replace('${toc_errors}', report_data['toc_errors'])
            report_html = report_html.replace('${test_classes_html}', report_data['test_classes_html'])

            # Write html content to an output file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_html)

            # Output logs
            logger.info(f"HTML report generated successfully: {output_path}")
            logger.info(f"Total tests: {report_data['total_tests']}")
            logger.info(f"Passed: {report_data['passed_tests']}, "
                        f"Failed: {report_data['failed_tests']}, "
                        f"Error: {report_data['error_tests']}, "
                        f"Skipped: {report_data['skipped_tests']}")

        @classmethod
        def run_report(cls, xml_path: str, template_path: str, output_path: str = ""):
            """
            (Public method) Executor for convert a junit xml report to html report,
            it can be called directly by other modules with arguments.

            Args:
                xml_path (str):
                    The path of junit xml file (e.g: "./test-results.xml").
                template_path (str):
                    The path of template html file (e.g: "./templates/email_report_template.html").
                output_path (str, optional):
                    The path of output html file (e.g: "./test-results-junit.html").
                    Optional, default to --xml-path .xml -> -junit.html.

            Examples:
                >>> cls.run_report(xml_path="./test-results.xml",
                ...                template_path="./templates/email_report_template.html",
                ...                output_path="./test-results-junit.html")
            """
            output_path = output_path if output_path else re.sub(r'\.xml$', '-junit.html', xml_path)
            report_data: dict = cls._parse_junit_xml(xml_path)
            cls._generate_html_report(template_path, report_data, output_path)

    @classmethod
    def main(cls):
        """
        Functions for run report directly by Python command.
        All params can be provided in cmd lines.
        --output-path is optional, default to --xml-path .xml -> -junit.html.

        Examples:
            pytest --junitxml=./test-results.xml
            python report_helper.py --report-type=junit --xml-path=./test-results.xml --template-path=./email_report_template.html
        """
        parser = argparse.ArgumentParser(description="Execute a test report converter")
        parser.add_argument(
            "--report-type",
            default="junit",
            help="Type of report to generate (Default: %(default)s)"
        )
        parser.add_argument(
            "--xml-path",
            default="test-results.xml",
            help="Input path of JUnit XML report (Default: %(default)s)"
        )
        parser.add_argument(
            "--template-path",
            default="email_report_template.html",
            help="Input path of HTML template (Default: %(default)s)"
        )
        parser.add_argument(
            "--output-path",
            default="",
            help="Output path of generated HTML reports (Default: %(default)s)"
        )
        args = parser.parse_args()

        if "junit" == args.report_type:
            output_path = args.output_path if args.output_path else re.sub(r'\.xml$', '-junit.html', args.xml_path)
            cls.JunitToHtmlConverter.run_report(
                xml_path=args.xml_path,
                template_path=args.template_path,
                output_path=output_path
            )
        else:
            raise ValueError(f"Invalid report type: {args.report_type}.")


if __name__ == "__main__":
    HtmlReportHelper.main()
