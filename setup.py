from setuptools import setup, find_packages

setup(
    name="agent-builder",
    version="1.0.0",
    description="Agent Calling Agent Builder — multi-agent orchestrator for Hermes Desktop App",
    author="tarisayulianti",
    py_modules=["orca", "status_tracker", "hermes_client", "spawn_agent2_inner"],
    python_requires=">=3.11",
    install_requires=[],  # all stdlib
    entry_points={
        "console_scripts": [
            "agent-builder=orca:main",
        ],
    },
)
