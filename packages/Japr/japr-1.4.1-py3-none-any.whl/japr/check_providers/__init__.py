from japr.check_providers.readme_check_provider import ReadmeCheckProvider
from japr.check_providers.license_check_provider import LicenseCheckProvider
from japr.check_providers.git_check_provider import GitCheckProvider
from japr.check_providers.ci_check_provider import CiCheckProvider
from japr.check_providers.python_check_provider import PythonCheckProvider
from japr.check_providers.github_check_provider import GitHubCheckProvider
from japr.check_providers.csharp_check_provider import CSharpCheckProvider
from japr.check_providers.contributing_check_provider import ContributingCheckProvider
from japr.check_providers.javascript_check_provider import JavascriptCheckProvider
from japr.check_providers.rust_check_provider import RustCheckProvider
from japr.check_providers.terraform_check_provider import TerraformCheckProvider
from japr.check_providers.shell_check_provider import ShellCheckProvider

check_providers = [
    ReadmeCheckProvider(),
    LicenseCheckProvider(),
    GitCheckProvider(),
    CiCheckProvider(),
    PythonCheckProvider(),
    GitHubCheckProvider(),
    CSharpCheckProvider(),
    ContributingCheckProvider(),
    JavascriptCheckProvider(),
    RustCheckProvider(),
    TerraformCheckProvider(),
    ShellCheckProvider(),
]
