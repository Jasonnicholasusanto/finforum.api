from sqlmodel import Session, select
from app.models.navbar_routes import NavbarRoute
from app.schemas.navbar_routes import NavbarRoutes, NavbarRouteBase

def get_navbar_routes(session: Session) -> NavbarRoutes:
    """
    Retrieve all active navbar routes from the database.
    """
    routes = session.exec(
        select(NavbarRoute)
        .where(NavbarRoute.is_visible)
        .order_by(NavbarRoute.order_index)
    ).all()

    route_list = [
        NavbarRouteBase.model_validate(r, from_attributes=True)
        for r in routes
    ]

    return NavbarRoutes(navbar_routes=route_list)
