#  Copyright 2025 European Union
#  Author: Bulgheroni Antonio (antonio.bulgheroni@ec.europa.eu)
#  SPDX-License-Identifier: EUPL-1.2
"""
Unit tests for db_filter module.
"""

import operator
import warnings
from unittest.mock import Mock, patch

import pytest
from peewee import AutoField, BooleanField, IntegerField, Model, TextField

from mafw.db.db_filter import Filter, FilterRegister


# Mock Model classes for testing
class MockModel(Model):
    """Mock model for testing."""

    id = AutoField(primary_key=True)
    name = TextField()
    active = BooleanField()
    count = IntegerField()

    class Meta:
        database = Mock()


class AnotherMockModel(Model):
    """Another mock model for testing."""

    id = AutoField(primary_key=True)
    description = TextField()

    class Meta:
        database = Mock()


class LastMockModel(Model):
    """Another mock model for testing."""

    id = AutoField(primary_key=True)
    description = TextField()

    class Meta:
        database = Mock()


class TestFilter:
    """Test cases for the Filter class."""

    @pytest.fixture
    def basic_filter(self):
        """Basic filter fixture."""
        return Filter('TestProcessor.Filter.TestModel', name='test*', active=True, count=[1, 2, 3])

    @pytest.fixture
    def bound_filter(self):
        """Filter bound to a model."""
        flt = Filter('TestProcessor.Filter.MockModel', name='test*', active=True, count=[1, 2, 3])
        flt.bind(MockModel)
        return flt

    def test_init_basic(self):
        """Test basic Filter initialization."""
        flt = Filter('TestProcessor.Filter.TestModel')
        assert flt.name == 'TestProcessor.Filter.TestModel'
        assert flt.model_name == 'TestModel'
        assert flt.model is None
        assert not flt._model_bound
        assert flt._fields == {}

    def test_init_with_kwargs(self):
        """Test Filter initialization with keyword arguments."""
        flt = Filter('TestProcessor.Filter.TestModel', active=True, count=42)
        assert flt.name == 'TestProcessor.Filter.TestModel'
        assert flt.model_name == 'TestModel'
        assert flt._fields == {'active': True, 'count': 42}
        assert flt.get_field('active') is True
        assert flt.get_field('count') == 42

    @pytest.mark.parametrize(
        'name,expected_model_name',
        [
            ('Processor.Filter.Model', 'Model'),
            ('Simple', 'Simple'),
            ('A.B.C.D', 'D'),
            ('Processor.Filter.ComplexModelName', 'ComplexModelName'),
        ],
    )
    def test_model_name_extraction(self, name, expected_model_name):
        """Test model name extraction from filter name."""
        flt = Filter(name)
        assert flt.model_name == expected_model_name

    def test_bind_with_model(self):
        """Test binding filter to a specific model."""
        flt = Filter('TestProcessor.Filter.TestModel')
        flt.bind(MockModel)
        assert flt.model == MockModel
        assert flt.is_bound

    def test_bind_without_model_success(self):
        """Test binding filter without model parameter when model exists in globals."""
        flt = Filter('TestProcessor.Filter.MockModel')
        with patch('mafw.db.db_filter.globals', return_value={'MockModel': MockModel}):
            flt.bind()
            assert flt.model == MockModel
            assert flt.is_bound

    def test_bind_without_model_failure(self):
        """Test binding filter without model parameter when model doesn't exist in globals."""
        flt = Filter('TestProcessor.Filter.NonExistentModel')
        with patch('mafw.db.db_filter.globals', return_value={}):
            flt.bind()
            assert flt.model is None
            assert not flt.is_bound

    def test_is_bound_property(self):
        """Test is_bound property."""
        flt = Filter('TestProcessor.Filter.TestModel')
        assert not flt.is_bound
        flt.bind(MockModel)
        assert flt.is_bound

    def test_get_field_success(self, basic_filter):
        """Test getting existing field."""
        assert basic_filter.get_field('name') == 'test*'
        assert basic_filter.get_field('active') is True
        assert basic_filter.get_field('count') == [1, 2, 3]

    def test_get_field_failure(self, basic_filter):
        """Test getting non-existent field raises KeyError."""
        with pytest.raises(KeyError):
            basic_filter.get_field('nonexistent')

    def test_set_field(self, basic_filter):
        """Test setting field value."""
        basic_filter.set_field('new_field', 'new_value')
        assert basic_filter.get_field('new_field') == 'new_value'
        assert 'new_field' in basic_filter._fields

        # Test updating existing field
        basic_filter.set_field('name', 'updated*')
        assert basic_filter.get_field('name') == 'updated*'

    def test_field_names_property(self, basic_filter):
        """Test field_names property."""
        expected_names = ['name', 'active', 'count']
        assert set(basic_filter.field_names) == set(expected_names)
        assert len(basic_filter.field_names) == 3

    @pytest.mark.parametrize(
        'conf,name,expected_params',
        [
            # Standard dotted notation with matching config
            (
                {'TestProc': {'Filter': {'TestModel': {'field1': 'value1', 'field2': 42}}}},
                'TestProc.Filter.TestModel',
                {'field1': 'value1', 'field2': 42},
            ),
            # Non-existent processor
            ({'OtherProc': {'Filter': {'TestModel': {'field1': 'value1'}}}}, 'TestProc.Filter.TestModel', {}),
            # Non-standard name format
            ({'TestProc': {'Filter': {'TestModel': {'field1': 'value1'}}}}, 'SimpleFilter', {}),
            # With default configuration
            (
                {'TestProc': {'Filter': {'TestModel': {'field1': 'overridden'}}}},
                'TestProc.Filter.TestModel',
                {'default_field': 'default_value', 'field1': 'overridden'},
            ),
        ],
    )
    def test_from_conf(self, conf, name, expected_params):
        """Test creating Filter from configuration."""
        default = {'default_field': 'default_value'} if 'default_field' in str(expected_params) else None
        flt = Filter.from_conf(name, conf, default)

        assert flt.name == name
        for key, value in expected_params.items():
            assert flt.get_field(key) == value

    def test_from_conf_with_copy(self):
        """Test that from_conf creates a copy of the configuration."""
        original_conf = {'field1': 'value1'}
        conf = {'TestProc': {'Filter': {'TestModel': original_conf}}}

        flt = Filter.from_conf('TestProc.Filter.TestModel', conf)
        flt.set_field('field1', 'modified')

        # Original config should not be modified
        assert original_conf['field1'] == 'value1'

    def test_filter_unbound_warning(self):
        """Test filter method with unbound filter shows warning."""
        flt = Filter('TestProcessor.Filter.TestModel', name='test')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('always')
            result = flt.filter()

            assert len(w) == 1
            assert issubclass(w[0].category, UserWarning)
            assert 'Unable to generate the filter' in str(w[0].message)
            assert result is True

    def test_filter_bound_no_fields(self):
        """Test filter method with bound filter but no fields."""
        flt = Filter('TestProcessor.Filter.MockModel')
        flt.bind(MockModel)

        result = flt.filter()
        assert result is True

    def test_filter_bound_with_fields(self, bound_filter):
        """Test filter method with bound filter and fields."""
        # Mock the model fields and their methods
        mock_name_field = Mock()
        mock_active_field = Mock()
        mock_count_field = Mock()

        mock_name_field.__mod__ = Mock(return_value=True)
        mock_active_field.__eq__ = Mock(return_value=True)
        mock_count_field.in_ = Mock(return_value=True)

        # Set up the model to have these fields
        with (
            patch.object(MockModel, 'name', mock_name_field),
            patch.object(MockModel, 'active', mock_active_field),
            patch.object(MockModel, 'count', mock_count_field),
        ):
            bound_filter.filter()

            # Verify field operations were called correctly
            mock_name_field.__mod__.assert_called_once_with('test*')
            mock_active_field.__eq__.assert_called_once_with(True)
            mock_count_field.in_.assert_called_once_with([1, 2, 3])

    @pytest.mark.parametrize(
        'field_value,expected_operation',
        [
            (42, '__eq__'),  # int
            (3.14, '__eq__'),  # float
            (True, '__eq__'),  # bool
            ('test*', '__mod__'),  # string
            ([1, 2, 3], 'in_'),  # list
        ],
    )
    def test_filter_field_types(self, field_value, expected_operation):
        """Test filter method with different field value types."""
        flt = Filter('TestProcessor.Filter.MockModel', name=field_value)
        flt.bind(MockModel)

        mock_field = Mock()

        if expected_operation == 'in_':
            mock_field.in_ = Mock(return_value=True)
        elif expected_operation == '__mod__':
            mock_field.__mod__ = Mock(return_value=True)
        else:  # __eq__
            mock_field.__eq__ = Mock(return_value=True)

        with patch.object(MockModel, 'name', mock_field):
            flt.filter()

            if expected_operation == 'in_':
                mock_field.in_.assert_called_once_with(field_value)
            elif expected_operation == '__mod__':
                mock_field.__mod__.assert_called_once_with(field_value)
            else:
                mock_field.__eq__.assert_called_once_with(field_value)

    def test_filter_with_not_supported_value_type(self):
        flt = Filter('TestProcessor.Filter.MockModel', name={})
        flt.bind(MockModel)
        with pytest.raises(TypeError, match='Filter value of unsupported type'):
            flt.filter()

    def test_filter_nonexistent_model_field(self):
        """Test filter method ignores fields that don't exist on the model."""
        flt = Filter('TestProcessor.Filter.MockModel', nonexistent_field='value')
        flt.bind(MockModel)

        result = flt.filter()
        assert result is True  # Should return True when no valid fields


class TestFilterRegister:
    """Test cases for the FilterRegister class."""

    @pytest.fixture
    def empty_register(self):
        """Empty FilterRegister fixture."""
        return FilterRegister()

    @pytest.fixture
    def populated_register(self):
        """FilterRegister with some filters."""
        flt1 = Filter('Proc.Filter.MockModel', field1='value1')
        flt2 = Filter('Proc.Filter.AnotherMockModel', field2='value2')
        return FilterRegister({'MockModel': flt1, 'AnotherMockModel': flt2})

    def test_init_empty(self):
        """Test FilterRegister initialization without data."""
        register = FilterRegister()
        assert len(register) == 0
        assert register._global_filter == {}
        assert register.new_only is True  # Default value

    def test_init_with_data(self):
        """Test FilterRegister initialization with data."""
        flt = Filter('Test.Filter.Model', field='value')
        register = FilterRegister({'Model': flt})
        assert len(register) == 1
        assert register['Model'] == flt

    def test_new_only_property_default(self, empty_register):
        """Test new_only property default value."""
        assert empty_register.new_only is True

    def test_new_only_property_get_set(self, empty_register):
        """Test new_only property getter and setter."""
        empty_register.new_only = False
        assert empty_register.new_only is False
        assert empty_register._global_filter['new_only'] is False

        empty_register.new_only = True
        assert empty_register.new_only is True

    def test_new_only_property_from_global_filter(self):
        """Test new_only property when set in global filter."""
        register = FilterRegister()
        register._global_filter['new_only'] = False
        assert register.new_only is False

    def test_setitem_valid_filter(self, empty_register):
        """Test setting valid Filter object."""
        flt = Filter('Test.Filter.Model', field='value')
        empty_register['Model'] = flt
        assert empty_register['Model'] == flt
        assert len(empty_register) == 1

    def test_setitem_invalid_type(self, empty_register):
        """Test setting invalid type is silently ignored."""
        initial_len = len(empty_register)
        empty_register['Model'] = 'not a filter'
        empty_register['Model2'] = 42
        empty_register['Model3'] = None

        assert len(empty_register) == initial_len
        assert 'Model' not in empty_register
        assert 'Model2' not in empty_register
        assert 'Model3' not in empty_register

    def test_bind_all_with_list(self, populated_register):
        """Test bind_all method with list of models."""
        models = [MockModel, AnotherMockModel]

        # Mock the bind method on filters
        with (
            patch.object(populated_register['MockModel'], 'bind') as mock_bind1,
            patch.object(populated_register['AnotherMockModel'], 'bind') as mock_bind2,
        ):
            populated_register.bind_all(models)

            mock_bind1.assert_called_once_with(MockModel)
            mock_bind2.assert_called_once_with(AnotherMockModel)

    def test_bind_all_with_dict(self, populated_register):
        """Test bind_all method with dictionary of models."""
        models = {'MockModel': MockModel, 'AnotherMockModel': AnotherMockModel}

        with (
            patch.object(populated_register['MockModel'], 'bind') as mock_bind1,
            patch.object(populated_register['AnotherMockModel'], 'bind') as mock_bind2,
        ):
            populated_register.bind_all(models)

            mock_bind1.assert_called_once_with(MockModel)
            mock_bind2.assert_called_once_with(AnotherMockModel)

    def test_bind_all_creates_missing_filters(self, empty_register):
        """Test bind_all creates filters for models not in register."""
        models = {'NewModel': MockModel}
        empty_register._global_filter = {'default_field': 'default_value'}

        with patch.object(Filter, 'from_conf') as mock_from_conf:
            mock_filter = Mock(spec=Filter)
            mock_from_conf.return_value = mock_filter

            empty_register.bind_all(models)

            mock_from_conf.assert_called_once_with('NewModel', conf={}, default={'default_field': 'default_value'})
            assert 'NewModel' in empty_register
            mock_filter.bind.assert_called_once_with(MockModel)

    def test_bind_all_fallback_bind(self, populated_register):
        """Test bind_all falls back to parameterless bind when filter not in models dict."""
        # populated_register has 'Model1' and 'Model2' filters
        # but we only provide models for 'Model1'
        models = {'MockModel': MockModel}  # Only one model, but register has two filters

        with (
            patch.object(populated_register['MockModel'], 'bind') as mock_bind1,
            patch.object(populated_register['AnotherMockModel'], 'bind') as mock_bind2,
        ):
            populated_register.bind_all(models)

            # MockModel should bind with the provided model
            mock_bind1.assert_called_once_with(MockModel)
            # AnotherMockModel should fall back to parameterless bind (tries to find in globals)
            mock_bind2.assert_called_once_with()

    def test_bind_all_fallback_bind_more_models(self, populated_register):
        # the registry has two models, but the model dict has three.
        models = {'MockModel': MockModel, 'AnotherMockModel': AnotherMockModel, 'LastMockModel': LastMockModel}

        # Mock the existing filters
        with (
            patch.object(populated_register['MockModel'], 'bind') as mock_bind1,
            patch.object(populated_register['AnotherMockModel'], 'bind') as mock_bind2,
            patch.object(Filter, 'from_conf') as mock_from_conf,
        ):
            # Mock the new filter creation
            mock_new_filter = Mock(spec=Filter)
            mock_from_conf.return_value = mock_new_filter

            populated_register.bind_all(models)

            # Assert register now has three items
            assert len(populated_register) == 3
            assert 'MockModel' in populated_register
            assert 'AnotherMockModel' in populated_register
            assert 'LastMockModel' in populated_register

            # Assert existing filters were bound with their models
            mock_bind1.assert_called_once_with(MockModel)
            mock_bind2.assert_called_once_with(AnotherMockModel)

            # Assert new filter was created and bound
            mock_from_conf.assert_called_once_with('LastMockModel', conf={}, default=populated_register._global_filter)
            mock_new_filter.bind.assert_called_once_with(LastMockModel)

    def test_filter_all_empty(self, empty_register):
        """Test filter_all with empty register."""
        result = empty_register.filter_all()
        assert result is True

    def test_filter_all_with_bound_filters(self, populated_register):
        """Test filter_all with bound filters."""
        # Mock the filters and their filter methods
        mock_expr1 = Mock()
        mock_expr2 = Mock()

        populated_register['MockModel'].filter = Mock(return_value=mock_expr1)
        populated_register['MockModel']._model_bound = True  # fake binding
        populated_register['AnotherMockModel'].filter = Mock(return_value=mock_expr2)
        populated_register['AnotherMockModel']._model_bound = True  # fake binding

        with patch('mafw.db.db_filter.reduce') as mock_reduce:
            mock_reduce.return_value = 'combined_expression'

            result = populated_register.filter_all()

            mock_reduce.assert_called_once_with(operator.and_, [mock_expr1, mock_expr2], True)
            assert result == 'combined_expression'

    def test_filter_all_with_unbound_filters(self, populated_register):
        """Test filter_all ignores unbound filters."""
        mock_expr1 = Mock()

        populated_register['MockModel'].filter = Mock(return_value=mock_expr1)
        populated_register['MockModel']._model_bound = True  # fake binding
        populated_register['AnotherMockModel'].filter = Mock(return_value=Mock())
        assert not populated_register['AnotherMockModel'].is_bound  # not bound

        with patch('mafw.db.db_filter.reduce') as mock_reduce:
            mock_reduce.return_value = 'single_expression'

            result = populated_register.filter_all()

            # Should only include the bound filter
            mock_reduce.assert_called_once_with(operator.and_, [mock_expr1], True)
            assert result == 'single_expression'

    def test_filter_all_no_bound_filters(self, populated_register):
        """Test filter_all when no filters are bound."""
        assert not populated_register['MockModel'].is_bound
        assert not populated_register['AnotherMockModel'].is_bound

        result = populated_register.filter_all()
        assert result is True


@pytest.mark.integration_test
class TestIntegration:
    """Integration tests combining Filter and FilterRegister."""

    def test_filter_register_workflow(self):
        """Test typical workflow with FilterRegister and Filter."""
        # Create configuration
        conf = {
            'TestProcessor': {
                'Filter': {
                    'MockModel': {'name': 'test*', 'active': True},
                    'AnotherMockModel': {'description': 'sample'},
                }
            }
        }

        # Create filters from configuration
        flt1 = Filter.from_conf('TestProcessor.Filter.MockModel', conf)
        flt2 = Filter.from_conf('TestProcessor.Filter.AnotherMockModel', conf)

        # Create register and add filters
        register = FilterRegister()
        register['MockModel'] = flt1
        register['AnotherMockModel'] = flt2

        # Bind all filters
        models = [MockModel, AnotherMockModel]
        register.bind_all(models)

        # Verify filters are bound
        assert register['MockModel'].is_bound
        assert register['AnotherMockModel'].is_bound

        # Verify filter generation works
        assert register['MockModel'].filter() is not True  # Should generate expressions
        assert register['AnotherMockModel'].filter() is not True

    @pytest.mark.parametrize(
        'global_new_only,expected',
        [
            (True, True),
            (False, False),
            (None, True),  # Default value
        ],
    )
    def test_global_filter_new_only_integration(self, global_new_only, expected):
        """Test global filter new_only flag integration."""
        register = FilterRegister()
        if global_new_only is not None:
            register.new_only = global_new_only

        assert register.new_only == expected
