import logging
import unittest
from unittest.mock import patch

from pyramid.tools.configuration.configuration import Configuration

class ConfigurationTest(unittest.TestCase):
	def setUp(self):
		self.config = Configuration()

	def test_default_logger(self):
		self.assertIsNotNone(logging.getLogger("config"))
		self.assertEqual(logging.getLogger("config").name, "config")

	@patch("pyramid.tools.configuration.configuration_load.ConfigurationFromEnv._get_env_vars")
	@patch("pyramid.tools.configuration.configuration_load.ConfigurationFromYAML._get_file_vars")
	@patch("pyramid.tools.configuration.configuration_load.ConfigurationFromYAML._validate_all")
	@patch("pyramid.tools.configuration.configuration_load.ConfigurationFromYAML._transform_all")
	def test_load_success(
		self, mock_transform_all, mock_validate_all, mock_get_file_vars, mock_get_env_vars
	):
		mock_transform_all.return_value = [1] * 9
		mock_validate_all.return_value = True
		mock_get_env_vars.return_value = {}
		mock_get_file_vars.return_value = {}

		result = self.config.load()

		self.assertTrue(result)
		mock_get_env_vars.assert_called_once()
		mock_get_file_vars.assert_called_once()
		mock_transform_all.assert_called()
		mock_validate_all.assert_called()

	@patch("pyramid.tools.configuration.configuration_load.ConfigurationFromEnv._get_env_vars")
	@patch("pyramid.tools.configuration.configuration_load.ConfigurationFromYAML._get_file_vars")
	@patch("pyramid.tools.configuration.configuration_load.ConfigurationFromYAML._validate_all")
	@patch("pyramid.tools.configuration.configuration_load.ConfigurationFromYAML._transform_all")
	def test_load_failure(
		self, mock_transform_all, mock_validate_all, mock_get_file_vars, mock_get_env_vars
	):
		mock_transform_all.return_value = [1] * 9
		mock_validate_all.return_value = False
		mock_get_env_vars.return_value = {}
		mock_get_file_vars.return_value = {}

		result = self.config.load("bad_config.yml")

		self.assertFalse(result)
		mock_get_env_vars.assert_called_once()
		mock_get_file_vars.assert_called_once()
		mock_transform_all.assert_called()
		mock_validate_all.assert_called()

	@patch("pyramid.tools.configuration.configuration_save.ConfigurationToYAML._save_to_yaml")
	def test_save(self, mock_save_to_yaml):
		file_name = "test_config.yml"
		self.config.save(file_name)
		mock_save_to_yaml.assert_called_once_with(file_name)
