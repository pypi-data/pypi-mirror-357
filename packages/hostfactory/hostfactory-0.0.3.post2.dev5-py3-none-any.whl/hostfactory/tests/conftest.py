"""Morgan Stanley makes this available to you under the Apache License,
Version 2.0 (the "License"). You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0. See the NOTICE file
distributed with this work for additional information regarding
copyright ownership. Unless required by applicable law or agreed
to in writing, software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
See the License for the specific language governing permissions and
limitations under the License. Watch and manage hostfactory machine
requests and pods in a Kubernetes cluster.

Test configuration for regression testing
"""

import pytest


def pytest_addoption(parser):
    """Add options to the pytest parser."""
    parser.addoption(
        "--flavor",
        action="store",
        default="vanilla",
        help="Flavor of the regression test.",
    )


@pytest.fixture
def flavor(request):
    """Fixture to get the flavor of the regression test."""
    return request.config.getoption("--flavor")
