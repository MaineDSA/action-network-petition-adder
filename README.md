[![CodeQL](https://github.com/MaineDSA/action-network-petition-adder/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/MaineDSA/action-network-petition-adder/actions/workflows/github-code-scanning/codeql)
[![Python checks](https://github.com/MaineDSA/action-network-petition-adder/actions/workflows/python-checks.yml/badge.svg)](https://github.com/MaineDSA/action-network-petition-adder/actions/workflows/python-checks.yml)
[![Coverage badge](https://raw.githubusercontent.com/MaineDSA/action-network-petition-adder/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/MaineDSA/action-network-petition-adder/blob/python-coverage-comment-action-data/htmlcov/index.html)

# Action Network Action Adder
Adds activists from a CSV to an Action Network action.
CSV file must have column names corresponding to the HTML field names in Action Network.
Field names in Action Network that aren't found in the CSV will be left blank.
If Action Network group has Affirmative Opt-In enabled, the default behavior is to add activists without email subscription.
To opt-in with affirmative opt-in enabled, add a CSV column with header name "opt_in". Activists with a empty cell or "no" in this column will not be opted in. Activists with anything else will be opted in.
