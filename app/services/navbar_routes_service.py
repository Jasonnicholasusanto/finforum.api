from sqlmodel import Session, select
from app.models.navbar_routes import NavbarRoute
from app.schemas.navbar_routes import NavbarRoutes, NavbarRouteBase


def get_navbar_routes(session: Session) -> NavbarRoutes:
    """
    Retrieve all visible navbar routes from the database and return them in a nested tree structure.
    """
    # 1. Fetch all visible routes ordered by order_index
    routes = session.exec(
        select(NavbarRoute)
        .where(NavbarRoute.is_visible)
        .order_by(NavbarRoute.order_index)
    ).all()

    # 2. Convert SQLModel rows to Pydantic schema objects
    route_list = [
        NavbarRouteBase.model_validate(r, from_attributes=True) for r in routes
    ]

    # 3. Build lookup map (id to route)
    schema_map = {
        r.id: schema for r, schema in zip(routes, route_list) if hasattr(r, "id")
    }

    # 4. Build nested tree
    root_routes = []
    for route in routes:
        schema = schema_map.get(route.id)
        if route.parent_id:
            parent_schema = schema_map.get(route.parent_id)
            if parent_schema:
                if parent_schema.children is None:
                    parent_schema.children = []
                parent_schema.children.append(schema)
        else:
            root_routes.append(schema)

    # 5. Return structured response
    return NavbarRoutes(navbar_routes=root_routes)
