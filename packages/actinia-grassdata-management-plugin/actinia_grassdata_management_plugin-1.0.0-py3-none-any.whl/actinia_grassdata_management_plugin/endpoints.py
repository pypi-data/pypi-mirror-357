#!/usr/bin/env python
"""Copyright (c) 2018-2025 mundialis GmbH & Co. KG.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Add endpoints to flask app with endpoint definitions and routes
"""

__license__ = "GPLv3"
__author__ = "Carmen Tawalika, Anika Weinmann"
__copyright__ = "Copyright 2022-2024 mundialis GmbH & Co. KG"
__maintainer__ = "mundialis GmbH & Co. KG"

from flask_restful_swagger_2 import Api, Resource

from actinia_grassdata_management_plugin.rest.map_layer_management import (
    RasterLayersResource,
)
from actinia_grassdata_management_plugin.rest.map_layer_management import (
    VectorLayersResource,
)
from actinia_grassdata_management_plugin.rest.raster_colors import (
    SyncPersistentRasterColorsResource,
)
from actinia_grassdata_management_plugin.rest.raster_layer import (
    RasterLayerResource,
)
from actinia_grassdata_management_plugin.rest.raster_legend import (
    SyncEphemeralRasterLegendResource,
)
from actinia_grassdata_management_plugin.rest.raster_renderer import (
    SyncEphemeralRasterRendererResource,
)
from actinia_grassdata_management_plugin.rest.raster_renderer import (
    SyncEphemeralRasterRGBRendererResource,
)
from actinia_grassdata_management_plugin.rest.raster_renderer import (
    SyncEphemeralRasterShapeRendererResource,
)
from actinia_grassdata_management_plugin.rest.strds_management import (
    STRDSManagementResource,
    SyncSTRDSListerResource,
)
from actinia_grassdata_management_plugin.rest.strds_raster_management import (
    STRDSRasterManagement,
)
from actinia_grassdata_management_plugin.rest.strds_renderer import (
    SyncEphemeralSTRDSRendererResource,
)
from actinia_grassdata_management_plugin.rest.vector_layer import (
    VectorLayerResource,
)
from actinia_grassdata_management_plugin.rest.vector_renderer import (
    SyncEphemeralVectorRendererResource,
)


def get_endpoint_class_name(
    endpoint_class: Resource,
    projects_url_part: str = "projects",
) -> str:
    """Create the name for the given endpoint class."""
    endpoint_class_name = endpoint_class.__name__.lower()
    if projects_url_part != "projects":
        name = f"{endpoint_class_name}_{projects_url_part}"
    else:
        name = endpoint_class_name
    return name


def create_project_endpoints(
    flask_api: Api,
    projects_url_part: str = "projects",
) -> None:
    """Add resources with "project" inside the endpoint url to the api.

    Args:
        apidoc (Api): Flask api
        projects_url_part (str): The name of the projects inside the endpoint
                                 URL; to add deprecated location endpoints set
                                 it to "locations"

    """

    # Raster management
    flask_api.add_resource(
        RasterLayersResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers",
        endpoint=get_endpoint_class_name(
            RasterLayersResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        RasterLayerResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>",
        endpoint=get_endpoint_class_name(
            RasterLayerResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralRasterLegendResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>/legend",
        endpoint=get_endpoint_class_name(
            SyncEphemeralRasterLegendResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncPersistentRasterColorsResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>/colors",
        endpoint=get_endpoint_class_name(
            SyncPersistentRasterColorsResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralRasterRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/raster_layers/<string:raster_name>/render",
        endpoint=get_endpoint_class_name(
            SyncEphemeralRasterRendererResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralRasterRGBRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/render_rgb",
        endpoint=get_endpoint_class_name(
            SyncEphemeralRasterRGBRendererResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralRasterShapeRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/render_shade",
        endpoint=get_endpoint_class_name(
            SyncEphemeralRasterShapeRendererResource, projects_url_part
        ),
    )
    # STRDS management
    flask_api.add_resource(
        SyncSTRDSListerResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/strds",
        endpoint=get_endpoint_class_name(
            SyncSTRDSListerResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        STRDSManagementResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/strds/<string:strds_name>",
        endpoint=get_endpoint_class_name(
            STRDSManagementResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        STRDSRasterManagement,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/strds/<string:strds_name>/raster_layers",
        endpoint=get_endpoint_class_name(
            STRDSRasterManagement, projects_url_part
        ),
    )
    # Vector management
    flask_api.add_resource(
        VectorLayersResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/vector_layers",
        endpoint=get_endpoint_class_name(
            VectorLayersResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        VectorLayerResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/vector_layers/<string:vector_name>",
        endpoint=get_endpoint_class_name(
            VectorLayerResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralVectorRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/vector_layers/<string:vector_name>/render",
        endpoint=get_endpoint_class_name(
            SyncEphemeralVectorRendererResource, projects_url_part
        ),
    )
    flask_api.add_resource(
        SyncEphemeralSTRDSRendererResource,
        f"/{projects_url_part}/<string:project_name>/mapsets/"
        "<string:mapset_name>/strds/<string:strds_name>/render",
        endpoint=get_endpoint_class_name(
            SyncEphemeralSTRDSRendererResource, projects_url_part
        ),
    )


#  endpoints loaded if run as actinia-core plugin as well as standalone app
def create_endpoints(flask_api: Api) -> None:
    """Create plugin endpoints."""

    # add deprecated location endpoints
    create_project_endpoints(flask_api, projects_url_part="locations")

    # add project endpoints
    create_project_endpoints(flask_api, projects_url_part="projects")
