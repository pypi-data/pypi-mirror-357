import json
from ...mcp_manager.client import ClientManagerMCP
from .steps.step import Step, StepMessage, DataStep, ResponseStep, QueryStep
from typing import Generator


class LLM:
    def __init__(self):
        self.client_manager_mcp: ClientManagerMCP = ClientManagerMCP()
        self.current_language: str = "English"

    def __call__(self, query: str) -> Generator[Step]:
        yield Step(step_type=StepMessage.ANALYZE_QUERY)

        processed_query: dict = self.preprocess_query(query=query)
        querys: list[str] = processed_query["querys"]
        self.current_language = processed_query["language"]

        yield DataStep(data={"querys": querys})

        for query in querys:
            for step in self.proccess_query(query):
                yield step

    def preprocess_query(self, query: str) -> dict:
        """
        Devuelve una lista con todas las querys en las que se divide la query principal y el lenguaje usado en la query. Puede ser solo una query
        """
        Exception("Not Implemented")

    def proccess_query(self, query: str, merge_count: int = 0) -> Generator[Step]:
        """
        ### Args
        - query: consulta
        - merge_count: cantidad de consultas anteriores que se uniran a la informacion de esta consulta
        """
        self.append_chat_history()
        yield QueryStep(query)
        yield Step(step_type=StepMessage.SELECT_SERVICE)
        # Cargar los servicios utiles
        service = json.loads(self.select_service(query))["service"]

        if len(service) == 0:
            yield DataStep(data={"service": None})
            yield ResponseStep(response=self.simple_query(query), data=None)
            return
        else:
            yield DataStep(data={"service": service})
            service = (
                self.client_manager_mcp.resources[service]
                if (self.client_manager_mcp.service_type(service) == "resource")
                else (
                    self.client_manager_mcp.tools[service]
                    if (self.client_manager_mcp.service_type(service) == "tool")
                    else None
                )
            )

        yield Step(step_type=StepMessage.CREATE_ARGUMENTS)
        args = json.loads(self.generate_args(query=query, service=service))["args"]
        data = service(args)[0].text
        yield DataStep(data={"args": args})
        
        response = self.final_response(query, data)
        yield ResponseStep(response=response, data=data)

    def append_chat_history(self):
        Exception("Not Implemented Exception")

    def simple_query(self, query: str) -> str:
        Exception("Not Implemented Exception")

    def select_service(self, query: str) -> str:
        Exception("Not Implemented Exception")

    def generate_args(self, query: str, service: str) -> str:
        Exception("Not Implemented Exception")

    def final_response(self, query: str, data: str | dict) -> str:
        Exception("Not Implemented Exception")


"""Call an Auth Admin method from Supabase Python SDK.\n\nThis tool provides a safe, validated interface to the Supabase Auth Admin SDK, allowing you to:\n- Manage users (create, update, delete)\n- List and search users\n- Generate authentication links\n- Manage multi-factor authentication\n- And more\n\nIMPORTANT NOTES:\n- Request bodies must adhere to the Python SDK specification\n- Some methods may have nested parameter structures\n- The tool validates all parameters against Pydantic models\n- Extra fields not defined in the models will be rejected\n\nAVAILABLE METHODS:\n- get_user_by_id: Retrieve a user by their ID\n- list_users: List all users with pagination\n- create_user: Create a new user\n- delete_user: Delete a user by their ID\n- invite_user_by_email: Send an invite link to a user\'s email\n- generate_link: Generate an email link for various authentication purposes\n- update_user_by_id: Update user attributes by ID\n- delete_factor: Delete a factor on a user\n\nEXAMPLES:\n1. Get user by ID:\n   method: "get_user_by_id"\n   params: {"uid": "user-uuid-here"}\n\n2. Create user:\n   method: "create_user"\n   params: {\n     "email": "user@example.com",\n     "password": "secure-password"\n   }\n\n3. Update user by ID:\n   method: "update_user_by_id"\n   params: {\n     "uid": "user-uuid-here",\n     "attributes": {\n       "email": "new@email.com"\n     }\n   }\n\nFor complete documentation of all methods and their parameters, use the get_auth_admin_methods_spec tool.\n"""
