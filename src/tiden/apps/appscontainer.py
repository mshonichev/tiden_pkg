#!/usr/bin/env python3

from ..tidenexception import TidenException
from .app import App

class AppsContainer:
    def __init__(self):
        self.apps = {}
        self.app_options = {}
        self.apps_created = False
        self.apps_packages = {}

    def add_app(self, app, **options):
        self.app_options[app] = {
            'options': options.copy()
        }

    def get_configured_apps(self):
        return sorted(self.app_options.keys())

    def get_running_apps(self):
        return sorted(self.apps.keys())

    def get_app(self, app_name):
        return self.apps[app_name]

    def get_app_options(self, app_name):
        return self.app_options.get(app_name, {}).get('options', {})

    def get_app_package(self, app_class_name, app_name):
        app_class_package_name = app_class_name.lower()
        if app_class_package_name not in self.apps_packages:
            try:
                app_pkg = __import__("tiden.apps.%s" % app_class_package_name, globals(), locals(), [app_class_name], 0)
                self.apps_packages[app_class_package_name] = app_pkg
            except ImportError as e:
                raise TidenException("Can't import application class %s for application %s from package %s: %s" % (
                    app_class_name, app_name.title(), "tiden.apps.%s.%s" % (app_class_package_name, app_class_name), e))
        else:
            app_pkg = self.apps_packages[app_class_package_name]
        return app_pkg

    def create_app(self, app_name, artf_name, config, ssh):
        app_class_name = app_name.title()
        app_options = self.get_app_options(app_name)
        if 'app_class_name' in app_options:
            app_class_name = app_options['app_class_name'].title()
        app_pkg = self.get_app_package(app_class_name, app_name)
        app_class = getattr(app_pkg, app_class_name)
        app: App = app_class(artf_name, config, ssh, **app_options)
        app.app_type = app_class_name.lower()
        self.apps[app_name] = app
        return app

    def get_app_by_type(self, app_type):
        apps = []
        for app in self.apps.keys():
            if self.apps[app].app_type == app_type:
                apps.append(self.apps[app])
        return apps

    def setup_configured_apps(self, config, ssh_pool):
        self.create_configured_apps(config, ssh_pool)
        for app_name in self.get_running_apps():
            app: App = self.get_app(app_name)
            if hasattr(app, 'setup'):
                app.setup()

    def check_requirements(self, config, ssh_pool):
        self.create_configured_apps(config, ssh_pool)
        for app_name in self.get_running_apps():
            app: App = self.get_app(app_name)
            if hasattr(app, 'check_requirements'):
                app.check_requirements()

    def create_configured_apps(self, config, ssh_pool):
        if self.apps_created:
            return
        for app_name in self.get_configured_apps():
            artf_found = False
            app_options = self.get_app_options(app_name)
            app_artifact_name = app_options.get('artifact_name', app_name)
            app_class_name = app_options.get('app_class_name', app_name).lower()

            # ... create one instance of application for each artifact of type equal to application name
            for artifact_name, artifact in config['artifacts'].items():
                if artifact_name == app_artifact_name and artifact.get('type') == app_class_name:
                    artf_found = True
                    self.create_app(app_name, artifact_name, config, ssh_pool)

            # if there were no specific artifacts configured, just create one instance of the application
            if not artf_found:
                self.create_app(app_name, app_name, config, ssh_pool)

        self.apps_created = True

    def teardown_running_apps(self):
        for app_name in self.get_running_apps():
            app: App = self.get_app(app_name)
            if hasattr(app, 'teardown'):
                app.teardown()

    def __str__(self):
        return ('\nConfigured apps: ' +
                ', '.join([
                    v.title() for v in self.get_configured_apps()
                ]) + '\n' +
                'Running apps:\n' +
                '\n'.join([
                    '  ' + app_name + ': ' + self.apps[app_name].app_type.title()
                    for app_name in sorted(self.apps.keys())
                ]) + '\n'
                )
