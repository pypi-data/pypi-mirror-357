import os
from sgqlc.operation import Operation
from sgqlc.endpoint.requests import RequestsEndpoint
from .schema import schema

class BlueAPIClient:
    """
    A client for interacting with the Blue API using GraphQL.

    This class provides methods to authenticate, execute queries and mutations,
    and perform specific operations like retrieving project names.
    """

    def __init__(self, token_id=None, secret_id=None, company_id=None, project_id=None):
        """
        Initialize the BlueAPIClient with authentication credentials.

        :param token_id: The token ID for authentication. If not provided, it will be read from the BLUE_TOKEN_ID environment variable.
        :param secret_id: The secret ID for authentication. If not provided, it will be read from the BLUE_SECRET_ID environment variable.
        :param company_id: The company ID. If not provided, it will be read from the BLUE_COMPANY_ID environment variable.
        :param project_id: The project ID. If not provided, it will be read from the BLUE_PROJECT_ID environment variable.
        """
        # Set credentials, prioritizing passed arguments over environment variables
        self.token_id = token_id or os.environ.get('BLUE_TOKEN_ID')
        self.secret_id = secret_id or os.environ.get('BLUE_SECRET_ID')
        self.company_id = company_id or os.environ.get('BLUE_COMPANY_ID')
        self.project_id = project_id or os.environ.get('BLUE_PROJECT_ID')

        # Validate that required credentials are provided
        if not all([self.token_id, self.secret_id, self.company_id]):
            raise ValueError("Missing required credentials. Please provide token_id, secret_id, and company_id.")

        # Prepare headers for API requests
        headers = {
            "x-bloo-token-id": self.token_id,
            "x-bloo-token-secret": self.secret_id,
        }
        if self.company_id:
            headers["x-bloo-company-id"] = self.company_id
        if self.project_id:
            headers["x-bloo-project-id"] = self.project_id

        # Initialize the GraphQL endpoint
        self.endpoint = RequestsEndpoint(
            "https://api.blue.cc/graphql",
            headers
        )

    def execute(self, operation):
        """
        Execute a GraphQL operation and return the result.

        :param operation: The GraphQL operation to execute.
        :return: The result of the operation.
        :raises RuntimeError: If the operation fails to execute.
        """
        try:
            data = self.endpoint(operation)
            return operation + data
        except Exception as e:
            # Catch any exceptions and raise a RuntimeError with a descriptive message
            raise RuntimeError(f"Failed to execute operation: {e}")

    def query(self):
        """
        Create and return a new GraphQL query operation.

        :return: A new Operation object for constructing queries.
        """
        return Operation(schema.Query)

    def mutation(self):
        """
        Create and return a new GraphQL mutation operation.

        :return: A new Operation object for constructing mutations.
        """
        return Operation(schema.Mutation)
    
    # Method to get project list
    def get_project_list(self, company_ids=None):
        """
        Get a list of projects for the specified company IDs.

        :param company_ids: List of company IDs to filter projects. If None, uses the client's company_id.
        :return: List of project objects containing project information.
        """
        op = self.query()
        filter_dict = {'companyIds': company_ids or [self.company_id]}
        projects = op.project_list(filter=filter_dict)
        projects.items.name()
        projects.items.id()
        result = self.execute(op)
        return result.project_list.items
    
    # Method to get lists
    def get_todo_lists(self, project_id):
        """
        Get all todo lists for a specific project.

        :param project_id: The ID of the project to fetch todo lists for.
        :return: List of todo list objects containing id, title, and position.
        """
        op = self.query()
        todo_lists = op.todo_lists(project_id=project_id)
        todo_lists.id()
        todo_lists.title()
        todo_lists.position()
        result = self.execute(op)
        return result.todo_lists
    