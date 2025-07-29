from pyrokinetics.kinetics import Kinetics, KineticsReaderJETTO
from pyrokinetics.species import Species
from pyrokinetics import template_dir
import pytest


class TestKineticsReaderJETTO:
    @pytest.fixture
    def jetto_reader(self):
        return KineticsReaderJETTO()

    @pytest.fixture
    def example_file(self):
        return template_dir / "jetto.jsp"

    def test_read_from_file(self, jetto_reader, example_file):
        """
        Ensure it can read the example JETTO file, and that it produces a Species dict.
        """
        result = jetto_reader(example_file)
        assert isinstance(result, Kinetics)
        for _, value in result.species_data.items():
            assert isinstance(value, Species)

    def test_verify_file_type(self, jetto_reader, example_file):
        """Ensure verify_file_type completes without throwing an error"""
        jetto_reader.verify_file_type(example_file)

    def test_read_file_does_not_exist(self, jetto_reader):
        """Ensure failure when given a non-existent file"""
        filename = template_dir / "helloworld"
        with pytest.raises((FileNotFoundError, ValueError)):
            jetto_reader(filename)

    def test_read_file_is_not_jsp(self, jetto_reader):
        """Ensure failure when given a non-netcdf file"""
        filename = template_dir / "input.gs2"
        with pytest.raises(ValueError):
            jetto_reader(filename)

    @pytest.mark.parametrize("filename", ["transp.cdf", "scene.cdf"])
    def test_read_file_is_not_jetto(self, jetto_reader, filename):
        """Ensure failure when given a non-jetto netcdf file

        This could fail for any number of reasons during processing.
        """
        filename = template_dir / filename
        with pytest.raises(Exception):
            jetto_reader(filename)

    def test_verify_file_does_not_exist(self, jetto_reader):
        """Ensure failure when given a non-existent file"""
        filename = template_dir / "helloworld"
        with pytest.raises((FileNotFoundError, ValueError)):
            jetto_reader.verify_file_type(filename)

    def test_verify_file_is_not_netcdf(self, jetto_reader):
        """Ensure failure when given a non-netcdf file"""
        filename = template_dir / "input.gs2"
        with pytest.raises(ValueError):
            jetto_reader.verify_file_type(filename)

    @pytest.mark.parametrize("filename", ["transp.cdf", "scene.cdf"])
    def test_verify_file_is_not_jetto(self, jetto_reader, filename):
        """Ensure failure when given a non-jetto netcdf file"""
        filename = template_dir / filename
        with pytest.raises(ValueError):
            jetto_reader.verify_file_type(filename)
