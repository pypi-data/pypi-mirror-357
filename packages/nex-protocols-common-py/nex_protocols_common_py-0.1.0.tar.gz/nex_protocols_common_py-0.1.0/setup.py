from setuptools import setup


setup(
    name="nex_protocols_common_py",
    version="0.1.0",
    description="Nintendo NEX protocols utilities for matchmaking, sessions, and gatherings.",
    author="Your Name",
    py_modules=[
        "authentication_protocol",
        "datastore_protocol",
        "matchmake_extension_protocol",
        "matchmaking_ext_protocol",
        "matchmaking_protocol",
        "matchmaking_utils",
        "nat_traversal_protocol",
        "ranking_protocol",
        "secure_connection_protocol"
    ],
    install_requires=[
        "pymongo",
        "bson"
    ],
    python_requires=">=3.7",
)