from titan_mind.utils.general.mcp import get_the_headers_from_the_current_mcp_request


def get_the_api_key()->str:
    api_key = get_the_headers_from_the_current_mcp_request().get("api-key")
    return api_key


def get_the_business_code()->str:
    business_code = get_the_headers_from_the_current_mcp_request().get("bus-code")
    return business_code