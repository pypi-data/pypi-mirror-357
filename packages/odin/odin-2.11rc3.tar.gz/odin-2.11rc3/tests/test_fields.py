import datetime
import enum
import pathlib
import re
import uuid
from copy import deepcopy

import pytest

import odin
from odin.datetimeutil import FixedTimezone
from odin.exceptions import ValidationError
from odin.fields import *
from odin.fields import Field, NotProvided, TimeStampField
from odin.fields.virtual import VirtualField
from odin.validators import (
    MaxLengthValidator,
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    RegexValidator,
)

utc = datetime.timezone.utc


class ObjectValue:
    pass


class ValidatorTest:
    message = "Default message"
    code = "test_code"

    def __init__(self, fail, *params):
        self.fail = fail
        self.params = params

    def __call__(self, value):
        if self.fail:
            raise ValidationError(
                code=self.code, message=self.message, params=self.params
            )


class FieldTest(Field):
    def to_python(self, value):
        return value


class DynamicTypeNameFieldTest(IntegerField):
    @staticmethod
    def data_type_name(instance):
        return "Foo"


class TestField:
    def test_error_messages_no_overrides(self):
        target = FieldTest()

        assert {
            "invalid_choice": "Value %r is not a valid choice.",
            "null": "This field cannot be null.",
            "required": "This field is required.",
        } == target.error_messages

    def test_error_messages_override_add(self):
        target = FieldTest(
            error_messages={
                "null": "Override",
                "other": "Other Value",
            }
        )

        assert {
            "invalid_choice": "Value %r is not a valid choice.",
            "null": "Override",
            "required": "This field is required.",
            "other": "Other Value",
        } == target.error_messages

    def test_set_attributes_from_name(self):
        target = FieldTest()
        target.set_attributes_from_name("test_name")

        assert "test_name" == target.name
        assert "test_name" == target.attname
        assert "test name" == target.verbose_name
        assert "test names" == target.verbose_name_plural

    def test_set_attributes_from_name_with_name(self):
        target = FieldTest(name="init_name")
        target.set_attributes_from_name("test_name")

        assert "init_name" == target.name
        assert "test_name" == target.attname
        assert "init name" == target.verbose_name
        assert "init names" == target.verbose_name_plural

    def test_set_attributes_from_name_with_verbose_name(self):
        target = FieldTest(verbose_name="init Verbose Name")
        target.set_attributes_from_name("test_name")

        assert "test_name" == target.name
        assert "test_name" == target.attname
        assert "init Verbose Name" == target.verbose_name
        assert "init Verbose Names" == target.verbose_name_plural

    @pytest.mark.parametrize(
        "value, expected",
        (
            (None, None),
            ("", ""),
            ("abc", "abc"),
            (1, "1"),
            (True, "True"),
            (False, "False"),
        ),
    )
    def test_as_string(self, value, expected):
        target = FieldTest()

        actual = target.as_string(value)

        assert actual == expected

    def test_choice_doc_test(self):
        target = FieldTest(
            choices=(
                ("a", "A Value"),
                ("b", "B Value"),
                ("c", "C Value"),
                ("d", "D Value"),
            )
        )

        assert target.choices_doc_text == target.choices

    def test_has_default(self):
        target = FieldTest()

        assert not target.has_default()

    def test_has_default_supplied(self):
        target = FieldTest(default="123")

        assert target.has_default()

    def test_get_default(self):
        target = FieldTest()

        assert target.get_default() is None

    def test_get_default_supplied(self):
        target = FieldTest(default="123")

        assert "123" == target.get_default()

    def test_get_default_callable(self):
        target = FieldTest(default=lambda: "321")

        assert "321" == target.get_default()

    def test_value_from_object(self):
        target = FieldTest()
        target.set_attributes_from_name("test_name")

        an_obj = ObjectValue()
        an_obj.test_name = "test_value"

        actual = target.value_from_object(an_obj)
        assert "test_value" == actual

    def test__repr(self):
        target = Field()
        assert "<odin.fields.Field>" == repr(target)
        target.set_attributes_from_name("eek")
        assert "<odin.fields.Field: eek>" == repr(target)

    def test__deep_copy(self):
        field = FieldTest(name="Test")
        target_copy = deepcopy(field)
        target_assign = field
        assert field is target_assign
        assert field is not target_copy
        assert field.name == target_copy.name

    def test_run_validators_and_override_validator_message(self):
        target = FieldTest(
            error_messages={"test_code": "Override message"},
            validators=[ValidatorTest(True)],
        )

        try:
            target.run_validators("Placeholder")
        except ValidationError as ve:
            assert "Override message" == ve.messages[0]
        else:
            raise AssertionError("Validation Error not raised.")

    def test_run_validators_and_override_validator_message_with_params(self):
        target = FieldTest(
            error_messages={"test_code": "Override message: %s"},
            validators=[ValidatorTest(True, "123")],
        )

        try:
            target.run_validators("Placeholder")
        except ValidationError as ve:
            assert ["Override message: 123"] == ve.messages
        else:
            raise AssertionError("Validation Error not raised.")

    def test_default_to_python_raises_not_implemented(self):
        target = Field()
        pytest.raises(NotImplementedError, target.to_python, "Anything...")

    def test_clean_uses_default_if_value_is_not_provided_is_true(self):
        target = FieldTest(use_default_if_not_provided=True, default="foo")
        actual = target.clean(NotProvided)
        assert "foo" == actual

    def test_clean_uses_default_if_value_is_not_provided_is_false(self):
        # Need to allow None as the if use_default_if_not_provided is false NOT_PROVIDED evaluates to None.
        target = FieldTest(use_default_if_not_provided=False, default="foo", null=True)
        actual = target.clean(NotProvided)
        assert actual is None


class VirtualFieldTest(VirtualField):
    pass


class TestVirtualField:
    def test_creation_counter(self):
        current_count = VirtualField.creation_counter
        next_count = current_count + 1
        target = VirtualField()

        assert VirtualField.creation_counter == next_count
        assert target.creation_counter == current_count
        assert hash(target) == current_count

    def test_repr(self):
        target = VirtualFieldTest()
        assert "<tests.test_fields.VirtualFieldTest>" == repr(target)
        target.set_attributes_from_name("eek")
        assert "<tests.test_fields.VirtualFieldTest: eek>" == repr(target)

    def test_default_descriptor_behaviour(self):
        class TestObj:
            test_field = VirtualField()

        target = TestObj()

        with pytest.raises(NotImplementedError):
            _ = target.test_field

        with pytest.raises(AttributeError) as excinfo:
            target.test_field = 123

        assert "Read only" == str(excinfo.value)


class TestFields:
    @staticmethod
    def assert_validator_in(validator_class, validators):
        """
        Assert that the specified validator is in the validation list.
        :param validator_class:
        :param validators:
        """
        for v in validators:
            if isinstance(v, validator_class):
                return
        raise AssertionError(
            "Validator %r was not found in list of validators." % validator_class
        )

    @staticmethod
    def assert_validator_not_in(validator_class, validators):
        """
        Assert that the specified validator is not in the validation list.
        :param validator_class:
        :param validators:
        """
        for v in validators:
            if isinstance(v, validator_class):
                raise AssertionError(
                    "Validator %r was found in list of validators." % validator_class
                )

    # BooleanField ############################################################

    @pytest.mark.parametrize(
        ("field", "value", "actual"),
        (
            (BooleanField(), True, True),
            (BooleanField(), 1, True),
            (BooleanField(), "Yes", True),
            (BooleanField(), "true", True),
            (BooleanField(), "T", True),
            (BooleanField(), "1", True),
            (BooleanField(), "TRUE", True),
            (BooleanField(), False, False),
            (BooleanField(), 0, False),
            (BooleanField(), "No", False),
            (BooleanField(), "false", False),
            (BooleanField(), "FALSE", False),
            (BooleanField(), "F", False),
            (BooleanField(), "0", False),
            (BooleanField(null=True), None, None),
        ),
    )
    def test_booleanfield_success(self, field, value, actual):
        assert field.clean(value) == actual

    @pytest.mark.parametrize(
        ("field", "value"),
        (
            (BooleanField(), None),
            (BooleanField(), ""),
            (BooleanField(), "Awesome!"),
        ),
    )
    def test_booleanfield_failure(self, field, value):
        with pytest.raises(ValidationError):
            field.clean(value)

    # StringField #############################################################

    @pytest.mark.parametrize(
        ("field", "value", "actual"),
        (
            (StringField(), "1", "1"),
            (StringField(), "eek", "eek"),
            (StringField(null=True), "1", "1"),
            (StringField(null=True), None, None),
            (StringField(null=True), "", ""),
            (StringField(null=True, empty=True), "", ""),
            (StringField(empty=True), "", ""),
            (StringField(max_length=10), "123456", "123456"),
        ),
    )
    def test_stringfield_success(self, field, value, actual):
        assert field.clean(value) == actual

    @pytest.mark.parametrize(
        ("field", "value"),
        (
            (StringField(), None),
            (StringField(), ""),
            (StringField(null=True, empty=False), ""),
            (StringField(empty=False), ""),
            (StringField(max_length=10), "1234567890a"),
        ),
    )
    def test_stringfield_failure(self, field, value):
        with pytest.raises(ValidationError):
            field.clean(value)

    def test_stringfield(self):
        f = StringField()
        assert f.max_length is None
        self.assert_validator_not_in(MaxLengthValidator, f.validators)

        f = StringField(max_length=10)
        assert f.max_length == 10
        self.assert_validator_in(MaxLengthValidator, f.validators)

    @pytest.mark.parametrize(
        ("field", "empty_value"),
        (
            (StringField(), False),
            (StringField(null=True), True),
            (StringField(null=False), False),
            (StringField(null=True, empty=True), True),
            (StringField(null=False, empty=True), True),
            (StringField(null=True, empty=False), False),
            (StringField(null=False, empty=False), False),
        ),
    )
    def test_stringfield__handling_of_null_empty(self, field, empty_value):
        assert field.empty == empty_value

    # URLField ################################################################

    def test_urlfield_1(self):
        f = UrlField()
        assert "http://www.github.com" == f.clean("http://www.github.com")
        pytest.raises(ValidationError, f.clean, "eek")
        pytest.raises(ValidationError, f.clean, None)
        assert f.max_length is None
        self.assert_validator_in(RegexValidator, f.validators)

    # IntegerField ############################################################

    def test_integerfield_1(self):
        f = IntegerField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        assert 123 == f.clean(123)
        assert 123 == f.clean("123")
        assert 123 == f.clean(123.5)
        assert None is f.min_value
        self.assert_validator_not_in(MinValueValidator, f.validators)
        assert None is f.max_value
        self.assert_validator_not_in(MaxValueValidator, f.validators)

    def test_integerfield_2(self):
        f = IntegerField(null=True)
        assert None is f.clean(None)
        pytest.raises(ValidationError, f.clean, "abc")
        assert 69 == f.clean(69)
        assert 69 == f.clean("69")
        assert 69 == f.clean(69.5)
        assert None is f.min_value
        self.assert_validator_not_in(MinValueValidator, f.validators)
        assert None is f.max_value
        self.assert_validator_not_in(MaxValueValidator, f.validators)

    def test_integerfield_3(self):
        f = IntegerField(min_value=50, max_value=100)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        assert 69 == f.clean(69)
        assert 69 == f.clean("69")
        assert 69 == f.clean(69.5)
        assert 50 == f.clean(50)
        assert 100 == f.clean(100)
        pytest.raises(ValidationError, f.clean, 30)
        pytest.raises(ValidationError, f.clean, 110)
        assert 50 == f.min_value
        self.assert_validator_in(MinValueValidator, f.validators)
        assert 100 == f.max_value
        self.assert_validator_in(MaxValueValidator, f.validators)

    # FloatField ##############################################################

    def test_floatfield_1(self):
        f = FloatField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        assert 123 == f.clean(123)
        assert 123.5 == f.clean("123.5")
        assert 123.5 == f.clean(123.5)
        assert None is f.min_value
        self.assert_validator_not_in(MinValueValidator, f.validators)
        assert None is f.max_value
        self.assert_validator_not_in(MaxValueValidator, f.validators)

    def test_floatfield_2(self):
        f = FloatField(null=True)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, "abc")
        assert 69 == f.clean(69)
        assert 69.5 == f.clean("69.5")
        assert 69.5 == f.clean(69.5)
        assert None is f.min_value
        self.assert_validator_not_in(MinValueValidator, f.validators)
        assert None is f.max_value
        self.assert_validator_not_in(MaxValueValidator, f.validators)

    def test_floatfield_3(self):
        f = FloatField(min_value=50.5, max_value=100.4)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        assert 69 == f.clean(69)
        assert 69.5 == f.clean("69.5")
        assert 69.5 == f.clean(69.5)
        assert 50.5 == f.clean(50.5)
        assert 100.4 == f.clean(100.4)
        pytest.raises(ValidationError, f.clean, 30)
        pytest.raises(ValidationError, f.clean, 110)
        assert 50.5 == f.min_value
        self.assert_validator_in(MinValueValidator, f.validators)
        assert 100.4 == f.max_value
        self.assert_validator_in(MaxValueValidator, f.validators)

    # DateField ###############################################################

    @pytest.mark.parametrize(
        "field,value,expected".split(","),
        (
            (DateField(), "2013-11-24", datetime.date(2013, 11, 24)),
            (DateField(), datetime.date(2013, 11, 24), datetime.date(2013, 11, 24)),
            (
                DateField(),
                datetime.datetime(2013, 11, 24, 1, 14),
                datetime.date(2013, 11, 24),
            ),
            (DateField(null=True), None, None),
        ),
    )
    def test_datefield_clean_success(self, field, value, expected):
        assert field.clean(value) == expected

    @pytest.mark.parametrize(
        "field,value".split(","),
        (
            (DateField(), None),
            (DateField(), "abc"),
            (DateField(), 123),
        ),
    )
    def test_datefield_clean_failure(self, field, value):
        pytest.raises(ValidationError, field.clean, value)

    @pytest.mark.parametrize(
        "field,value,expected".split(","),
        ((DateField(), datetime.date(2013, 11, 24), "2013-11-24"),),
    )
    def test_datefield_as_string(self, field, value, expected):
        assert field.as_string(value) == expected

    # TimeField ###############################################################

    def test_timefield_1(self):
        f = TimeField(assume_local=False)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.time(18, 43, tzinfo=utc) == f.clean("18:43:00.000Z")
        assert datetime.time(18, 43, tzinfo=utc) == f.clean(
            datetime.time(18, 43, tzinfo=utc)
        )

    def test_timefield_2(self):
        f = TimeField(assume_local=False, null=True)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.time(18, 43, tzinfo=utc) == f.clean("18:43:00.000Z")
        assert datetime.time(18, 43, tzinfo=utc) == f.clean(
            datetime.time(18, 43, tzinfo=utc)
        )

    @pytest.mark.parametrize(
        "field,value,expected".split(","),
        (
            (TimeField(), datetime.time(12, 44, 12, 12), "12:44:12.000012"),
            (TimeField(), datetime.time(12, 44, 12, 12, utc), "12:44:12.000012+00:00"),
        ),
    )
    def test_timefield_as_string(self, field, value, expected):
        assert field.as_string(value) == expected

    # NaiveTimeField ##########################################################

    @pytest.mark.parametrize(
        ("target", "value", "expected"),
        (
            (
                NaiveTimeField(ignore_timezone=False),
                "18:43:00.000Z",
                datetime.time(18, 43, tzinfo=utc),
            ),
            (
                NaiveTimeField(ignore_timezone=False),
                "18:43:00.000Z",
                datetime.time(18, 43, tzinfo=utc),
            ),
            (
                NaiveTimeField(ignore_timezone=False),
                datetime.time(18, 43, tzinfo=utc),
                datetime.time(18, 43, tzinfo=utc),
            ),
            (NaiveTimeField(ignore_timezone=False, null=True), None, None),
            (
                NaiveTimeField(ignore_timezone=False, null=True),
                "18:43:00.000Z",
                datetime.time(18, 43, tzinfo=utc),
            ),
            (
                NaiveTimeField(ignore_timezone=False, null=True),
                "18:43:00.000Z",
                datetime.time(18, 43, tzinfo=utc),
            ),
            (
                NaiveTimeField(ignore_timezone=False, null=True),
                datetime.time(18, 43, tzinfo=utc),
                datetime.time(18, 43, tzinfo=utc),
            ),
            (
                NaiveTimeField(ignore_timezone=True),
                "18:43:00.000Z",
                datetime.time(18, 43),
            ),
            (
                NaiveTimeField(ignore_timezone=True),
                "18:43:00.000Z",
                datetime.time(18, 43),
            ),
            (
                NaiveTimeField(ignore_timezone=True),
                datetime.time(18, 43, tzinfo=utc),
                datetime.time(18, 43),
            ),
        ),
    )
    def test_naivetimefield__clean_valid_values(self, target, value, expected):
        assert target.clean(value) == expected

    @pytest.mark.parametrize(
        ("target", "value"),
        (
            (NaiveTimeField(ignore_timezone=False), None),
            (NaiveTimeField(ignore_timezone=False), "abc"),
            (NaiveTimeField(ignore_timezone=False), 123),
            (NaiveTimeField(ignore_timezone=False, null=True), "abc"),
            (NaiveTimeField(ignore_timezone=False, null=True), 123),
            (NaiveTimeField(ignore_timezone=True), None),
            (NaiveTimeField(ignore_timezone=True), "abc"),
            (NaiveTimeField(ignore_timezone=True), 123),
        ),
    )
    def test_naivetimefield__clean_invalid_values(self, target, value):
        pytest.raises(ValidationError, target.clean, value)

    @pytest.mark.parametrize(
        ("target", "value", "expected"),
        (
            (
                NaiveTimeField(ignore_timezone=False),
                datetime.time(18, 43, tzinfo=utc),
                datetime.time(18, 43, tzinfo=utc),
            ),
            (
                NaiveTimeField(ignore_timezone=True),
                datetime.time(18, 43, tzinfo=utc),
                datetime.time(18, 43),
            ),
        ),
    )
    def test_naivetimefield__prepare(self, target, value, expected):
        assert target.prepare(value) == expected

    # DateTimeField ###########################################################

    def test_datetimefield_1(self):
        f = DateTimeField(assume_local=False)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            "2013-11-24T18:43:00.000Z"
        )
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            "2013-11-24 18:43:00.000Z"
        )
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)
        )

    def test_datetimefield_2(self):
        f = DateTimeField(assume_local=False, null=True)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            "2013-11-24T18:43:00.000Z"
        )
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            "2013-11-24 18:43:00.000Z"
        )
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)
        )

    @pytest.mark.parametrize(
        "field,value,expected".split(","),
        (
            (
                DateTimeField(),
                datetime.datetime(
                    2013, 11, 24, 18, 43, tzinfo=FixedTimezone.from_hours_minutes(10)
                ),
                "2013-11-24T18:43:00+10:00",
            ),
            (
                DateTimeField(),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                "2013-11-24T18:43:00+00:00",
            ),
        ),
    )
    def test_datetimefield_as_string(self, field, value, expected):
        assert field.as_string(value) == expected

    # NaiveDateTimeField ######################################################

    @pytest.mark.parametrize(
        ("target", "value", "expected"),
        (
            (
                NaiveDateTimeField(ignore_timezone=False),
                "2013-11-24T18:43:00.000Z",
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
            ),
            (
                NaiveDateTimeField(ignore_timezone=False),
                "2013-11-24 18:43:00.000Z",
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
            ),
            (
                NaiveDateTimeField(ignore_timezone=False),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
            ),
            (NaiveDateTimeField(ignore_timezone=False, null=True), None, None),
            (
                NaiveDateTimeField(ignore_timezone=False, null=True),
                "2013-11-24T18:43:00.000Z",
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
            ),
            (
                NaiveDateTimeField(ignore_timezone=False, null=True),
                "2013-11-24 18:43:00.000Z",
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
            ),
            (
                NaiveDateTimeField(ignore_timezone=False, null=True),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
            ),
            (
                NaiveDateTimeField(ignore_timezone=True),
                "2013-11-24T18:43:00.000Z",
                datetime.datetime(2013, 11, 24, 18, 43),
            ),
            (
                NaiveDateTimeField(ignore_timezone=True),
                "2013-11-24 18:43:00.000Z",
                datetime.datetime(2013, 11, 24, 18, 43),
            ),
            (
                NaiveDateTimeField(ignore_timezone=True),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                datetime.datetime(2013, 11, 24, 18, 43),
            ),
        ),
    )
    def test_naivedatetimefield__clean_valid_values(self, target, value, expected):
        assert target.clean(value) == expected

    @pytest.mark.parametrize(
        ("target", "value"),
        (
            (NaiveDateTimeField(ignore_timezone=False), None),
            (NaiveDateTimeField(ignore_timezone=False), "abc"),
            (NaiveDateTimeField(ignore_timezone=False), 123),
            (NaiveDateTimeField(ignore_timezone=False, null=True), "abc"),
            (NaiveDateTimeField(ignore_timezone=False, null=True), 123),
            (NaiveDateTimeField(ignore_timezone=True), None),
            (NaiveDateTimeField(ignore_timezone=True), "abc"),
            (NaiveDateTimeField(ignore_timezone=True), 123),
        ),
    )
    def test_naivedatetimefield__clean_invalid_values(self, target, value):
        pytest.raises(ValidationError, target.clean, value)

    @pytest.mark.parametrize(
        ("target", "value", "expected"),
        (
            (
                NaiveDateTimeField(ignore_timezone=False),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
            ),
            (
                NaiveDateTimeField(ignore_timezone=True),
                datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc),
                datetime.datetime(2013, 11, 24, 18, 43),
            ),
        ),
    )
    def test_naivedatetimefield__prepare(self, target, value, expected):
        assert target.prepare(value) == expected

    # HttpDateTimeField #######################################################

    def test_httpdatetimefield_1(self):
        f = HttpDateTimeField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=utc) == f.clean(
            "Wed Aug 29 17:12:58 +0000 2012"
        )
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)
        )

    def test_httpdatetimefield_2(self):
        f = HttpDateTimeField(null=True)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert datetime.datetime(2012, 8, 29, 17, 12, 58, tzinfo=utc) == f.clean(
            "Wed Aug 29 17:12:58 +0000 2012"
        )
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)
        )

    def test_httpdate_time_field__as_string(self):
        target = HttpDateTimeField()

        actual = target.as_string(datetime.datetime(2019, 6, 29, 8, 45, 23, tzinfo=utc))

        assert actual == "Sat, 29 Jun 2019 08:45:23 GMT"

    # TimeStampField ##########################################################

    def test_timestampfield_1(self):
        f = TimeStampField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, "Wed Aug 29 17:12:58 +0000 2012")
        assert datetime.datetime(1970, 1, 1, 0, 2, 3, tzinfo=utc) == f.clean(123)
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)
        )

    def test_timestampfield_2(self):
        f = TimeStampField(null=True)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, "Wed Aug 29 17:12:58 +0000 2012")
        assert datetime.datetime(1970, 1, 1, 0, 2, 3, tzinfo=utc) == f.clean(123)
        assert datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc) == f.clean(
            datetime.datetime(2013, 11, 24, 18, 43, tzinfo=utc)
        )

    def test_timestampfield_3(self):
        f = TimeStampField()
        assert f.prepare(None) is None
        assert 123 == f.prepare(datetime.datetime(1970, 1, 1, 0, 2, 3, tzinfo=utc))
        assert 123 == f.prepare(123)
        assert 123 == f.prepare(
            datetime.datetime(
                1970, 1, 1, 10, 2, 3, tzinfo=FixedTimezone.from_hours_minutes(10)
            )
        )

    # DictField ###############################################################

    def test_dictfield__where_null_is_false(self):
        f = DictField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert {} == f.clean({})
        assert {"foo": "bar"} == f.clean({"foo": "bar"})
        assert f.default == dict

    def test_dictfield__where_null_is_true(self):
        f = DictField(null=True)
        assert None is f.clean(None)
        assert {} == f.clean({})
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert {"foo": "bar"} == f.clean({"foo": "bar"})

    def test_dictfield__validators_are_executed_on_empty(self):
        """
        Ensure that validators are executed even if the field is empty
        """
        f = DictField(validators=[MinLengthValidator(1)])
        pytest.raises(ValidationError, f.clean, {})

    # ListField ##############################################################

    def test_listfield__where_null_is_false(self):
        f = ListField()
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert [] == f.clean([])
        assert ["foo", "bar"], f.clean(["foo" == "bar"])
        assert ["foo", "bar", "$", "eek"], f.clean(["foo", "bar", "$" == "eek"])
        assert f.default == list

    def test_listfield__where_null_is_true(self):
        f = ListField(null=True)
        assert None is f.clean(None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert [] == f.clean([])
        assert ["foo", "bar"], f.clean(["foo" == "bar"])
        assert ["foo", "bar", "$", "eek"], f.clean(["foo", "bar", "$" == "eek"])

    def test_listfield__validators_are_executed_on_empty(self):
        """
        Ensure that validators are executed even if the field is empty
        """
        f = ListField(validators=[MinLengthValidator(1)])
        pytest.raises(ValidationError, f.clean, [])

    # TypedListField #########################################################

    def test_typedlistfield__where_null_is_false(self):
        f = TypedListField(IntegerField())
        assert "List<Integer>" == f.data_type_name(f)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert [] == f.clean([])
        pytest.raises(ValidationError, f.clean, ["foo", "bar"])
        assert [1, 2, 3], f.clean([1, 2 == 3])
        assert f.default == list

    def test_typedlistfield__where_null_is_true(self):
        f = TypedListField(IntegerField(), null=True)
        assert "List<Integer>" == f.data_type_name(f)
        assert f.clean(None) is None
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert [] == f.clean([])
        pytest.raises(ValidationError, f.clean, ["foo", "bar"])
        assert [1, 2, 3], f.clean([1, 2 == 3])

    def test_typed_list_field__dynamic_type_name(self):
        f = TypedListField(DynamicTypeNameFieldTest(), null=True)
        assert "List<Foo>" == f.data_type_name(f)

    @pytest.mark.parametrize(
        "target, expected",
        (
            (TypedListField(IntegerField()), None),
            (
                TypedListField(
                    IntegerField(),
                    choices=[("these", "1"), ("are", "2"), ("bad", "3")],
                ),
                [("these", "1"), ("are", "2"), ("bad", "3")],
            ),
            (
                TypedListField(IntegerField(choices=((1, "1"), (2, "2"), (3, "3")))),
                ((1, "1"), (2, "2"), (3, "3")),
            ),
            (
                TypedListField(
                    IntegerField(choices=[("these", "1"), ("are", "2"), ("bad", "3")]),
                ),
                [("these", "1"), ("are", "2"), ("bad", "3")],
            ),
        ),
    )
    def test_typed_list_field__with_choices(self, target, expected):
        assert target.choices_doc_text == expected

    @pytest.mark.parametrize("value", ([None], [10, 11, 3], ["Fifteen"]))
    def test_typed_list_field__with_nested_validation_errors(self, value):
        target = TypedListField(IntegerField(min_value=10, null=False))
        pytest.raises(ValidationError, target.clean, value)

    # TypedDictField ##########################################################

    def test_typeddictfield_1(self):
        f = TypedDictField(IntegerField())
        assert "Dict<String, Integer>" == f.data_type_name(f)
        pytest.raises(ValidationError, f.clean, None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert {} == f.clean({})
        pytest.raises(ValidationError, f.clean, {"foo": "bar"})
        assert {"foo": 1} == f.clean({"foo": 1})

    def test_typeddictfield_2(self):
        f = TypedDictField(IntegerField(), null=True)
        assert "Dict<String, Integer>" == f.data_type_name(f)
        assert None is f.clean(None)
        pytest.raises(ValidationError, f.clean, "abc")
        pytest.raises(ValidationError, f.clean, 123)
        assert {} == f.clean({})
        pytest.raises(ValidationError, f.clean, {"foo": "bar"})
        assert {"foo": 1} == f.clean({"foo": 1})

    def test_typeddictfield_3(self):
        f = TypedDictField(StringField(), IntegerField(), null=True)
        assert "Dict<Integer, String>" == f.data_type_name(f)
        pytest.raises(ValidationError, f.clean, {"foo": "bar"})
        assert {1: "foo"} == f.clean({1: "foo"})

    def test_typeddictfield_nested_typed_array(self):
        f = TypedDictField(TypedArrayField(StringField()))
        assert "Dict<String, List<String>>" == f.data_type_name(f)
        assert {} == f.clean({})
        pytest.raises(ValidationError, f.clean, {"foo": "bar"})
        assert {"foo": ["bar", "eek"]}, f.clean({"foo": ["bar" == "eek"]})

    def test_typeddictfield_validate(self):
        f = TypedDictField(
            IntegerField(min_value=5),
            StringField(
                max_length=5,
                choices=[
                    ("foo", "Foo"),
                    ("bad_value", "Bad Value"),
                ],
            ),
        )
        assert "Dict<String, Integer>" == f.data_type_name(f)
        pytest.raises(ValidationError, f.clean, {None: 6})
        pytest.raises(ValidationError, f.clean, {"bad_value": 6})
        pytest.raises(ValidationError, f.clean, {"bar": 6})
        pytest.raises(ValidationError, f.clean, {"foo": None})
        pytest.raises(ValidationError, f.clean, {"foo": 2})

    def test_typed_dict_field_dynamic_type_name(self):
        f = TypedDictField(
            DynamicTypeNameFieldTest(),
            DynamicTypeNameFieldTest(),
        )
        assert "Dict<Foo, Foo>" == f.data_type_name(f)

    @pytest.mark.parametrize(
        "field value actual".split(),
        (
            (EmailField(), "foo@example.company", "foo@example.company"),
            (IPv4Field(), "127.0.0.1", "127.0.0.1"),
            (IPv6Field(), "::1", "::1"),
            (IPv6Field(), "1:2:3:4:5:6:7:8", "1:2:3:4:5:6:7:8"),
            (IPv46Field(), "127.0.0.1", "127.0.0.1"),
            (IPv46Field(), "::1", "::1"),
            (IPv46Field(), "1:2:3:4:5:6:7:8", "1:2:3:4:5:6:7:8"),
        ),
    )
    def test_valid_values(self, field, value, actual):
        assert field.clean(value) == actual

    # UUIDField ################################################################

    @pytest.mark.parametrize(
        "value",
        (
            uuid.uuid1(),
            uuid.uuid3(uuid.uuid4(), "name"),
            uuid.uuid4(),
            uuid.uuid5(uuid.uuid4(), "name"),
        ),
    )
    def test_uuid_field_with_uuid_objects(self, value):
        f = UUIDField()

        assert f.clean(value) == value

    @pytest.mark.parametrize(
        "value",
        (
            uuid.uuid1().bytes,
            uuid.uuid3(uuid.uuid4(), "name").bytes,
            uuid.uuid4().bytes,
            uuid.uuid5(uuid.uuid4(), "name").bytes,
        ),
        ids=(
            "bytes-uuid1",
            "bytes-uuid3",
            "bytes-uuid4",
            "bytes-uuid5",
        ),
    )
    def test_uuid_field_with_16_bytes_sequence(self, value):
        f = UUIDField()

        assert f.clean(value) == uuid.UUID(bytes=value)

    @pytest.mark.parametrize(
        "value",
        (
            str(uuid.uuid1()).encode("utf-8"),
            str(uuid.uuid3(uuid.uuid4(), "name")).encode("utf-8"),
            str(uuid.uuid4()).encode("utf-8"),
            str(uuid.uuid5(uuid.uuid4(), "name")).encode("utf-8"),
        ),
    )
    def test_uuid_field_with_bytes(self, value):
        f = UUIDField()

        assert f.clean(value) == uuid.UUID(value.decode("utf-8"))

    @pytest.mark.parametrize(
        "value",
        (
            str(uuid.uuid1()),
            str(uuid.uuid3(uuid.uuid4(), "name")),
            str(uuid.uuid4()),
            str(uuid.uuid5(uuid.uuid4(), "name")),
        ),
    )
    def test_uuid_field_with_string(self, value):
        f = UUIDField()

        assert f.clean(value) == uuid.UUID(value)

    @pytest.mark.parametrize("value", range(4))
    def test_uuid_field_with_int(self, value):
        f = UUIDField()

        assert f.clean(value) == uuid.UUID(int=value)

    @pytest.mark.parametrize("value", (-1, -2))
    def test_uuid_field_invalid_int(self, value):
        f = UUIDField()
        with pytest.raises(ValidationError):
            f.clean(value)

    @pytest.mark.parametrize(
        "value",
        (
            b"\254",
            b"\255",
        ),
    )
    def test_uuid_field_invalid_bytes(self, value):
        f = UUIDField()
        with pytest.raises(ValidationError):
            f.clean(value)

    @pytest.mark.parametrize(
        "value",
        (
            (1, 2, 3, 4, 5),
            [1, 2, 3, 4, 5],
            (-1, 2, 2, 2, 2, 2),
            [-1, 2, 2, 2, 2, 2],
            (2, -1, 2, 2, 2, 2),
            [2, -1, 2, 2, 2, 2],
        ),
    )
    def test_uuid_field_invalid_fields(self, value):
        f = UUIDField()
        with pytest.raises(ValidationError):
            f.clean(value)

    @pytest.mark.parametrize(
        "value", ("sometext", "01010101-0101-0101-0101-01010101010")
    )
    def test_uuid_field_invalid_hex(self, value):
        f = UUIDField()
        with pytest.raises(ValidationError):
            f.clean(value)

    def test_uuid_field_non_str_value(self):
        some_uuid = uuid.uuid4()

        class SomeObject:
            def __str__(self):
                return str(some_uuid)

        f = UUIDField()

        assert f.clean(SomeObject()) == some_uuid

    def test_uuid_field_invalid_non_str_value(self):
        class SomeObject:
            def __str__(self):
                return "sometext"

        f = UUIDField()

        with pytest.raises(ValidationError):
            f.clean(SomeObject())

    def test_uuid_field__none(self):
        f = UUIDField(null=True)

        assert f.clean(None) is None

    def test_uuid_field__not_none(self):
        f = UUIDField()

        with pytest.raises(ValidationError):
            f.clean(None)


class Colour(enum.Enum):
    Red = "red"
    Green = "green"
    Blue = "blue"


class Options(enum.Enum):
    Undefined = ""
    Yes = "True"
    No = "False"


class Number(enum.IntEnum):
    Thirteen = 13
    FortyTwo = 42
    SixtyNine = 69


class TestEnumField:
    @pytest.mark.parametrize(
        ("field", "value", "actual"),
        (
            (EnumField(Colour), "red", Colour.Red),
            (EnumField(Colour), "green", Colour.Green),
            (EnumField(Colour), Colour.Blue, Colour.Blue),
            (EnumField(Colour, null=True), None, None),
            (EnumField(Colour, null=True), "", None),
            (EnumField(Options), "", Options.Undefined),
            (EnumField(Number), 13, Number.Thirteen),
            (EnumField(Number), 42, Number.FortyTwo),
            (EnumField(Number), Number.SixtyNine, Number.SixtyNine),
            (EnumField(Number, null=True), None, None),
        ),
    )
    def test_to_python__valid(self, field, value, actual):
        assert field.clean(value) == actual

    @pytest.mark.parametrize(
        ("field", "value"),
        (
            (EnumField(Colour), "pink"),
            (EnumField(Colour), True),
            (EnumField(Colour), None),
            (EnumField(Colour), ""),
            (EnumField(Colour), Number.Thirteen),
            (EnumField(Number), "13"),
            (EnumField(Number), 14),
            (EnumField(Number), None),
        ),
    )
    def test_to_python__invalid(self, field, value):
        with pytest.raises(ValidationError):
            field.clean(value)

    @pytest.mark.parametrize(
        "field, value, actual",
        (
            (EnumField(Colour), "red", None),
            (EnumField(Colour), Colour.Blue, "blue"),
            (EnumField(Colour), None, None),
            (EnumField(Number), 13, None),
            (EnumField(Number), Number.FortyTwo, 42),
            (EnumField(Number), None, None),
        ),
    )
    def test_prepare(self, field, value, actual):
        assert field.prepare(value) == actual

    @pytest.mark.parametrize(
        "field, expected",
        (
            (
                EnumField(Colour),
                ((Colour.Red, "Red"), (Colour.Green, "Green"), (Colour.Blue, "Blue")),
            ),
            (
                EnumField(Number),
                (
                    (Number.Thirteen, "Thirteen"),
                    (Number.FortyTwo, "FortyTwo"),
                    (Number.SixtyNine, "SixtyNine"),
                ),
            ),
            (
                EnumField(Colour, choices=(Colour.Red, Colour.Blue)),
                ((Colour.Red, "Red"), (Colour.Blue, "Blue")),
            ),
        ),
    )
    @pytest.mark.skipif("sys.version_info.major < 3")
    def test_choices(self, field, expected):
        assert field.choices == expected

    @pytest.mark.parametrize(
        "field, expected",
        (
            (
                EnumField(Colour),
                {(Colour.Red, "Red"), (Colour.Green, "Green"), (Colour.Blue, "Blue")},
            ),
            (
                EnumField(Number),
                {
                    (Number.Thirteen, "Thirteen"),
                    (Number.FortyTwo, "FortyTwo"),
                    (Number.SixtyNine, "SixtyNine"),
                },
            ),
            (
                EnumField(Colour, choices=(Colour.Red, Colour.Blue)),
                {(Colour.Red, "Red"), (Colour.Blue, "Blue")},
            ),
        ),
    )
    def test_choices__with_set(self, field, expected):
        """Use sets to handle random ordering in earlier Python releases"""
        assert set(field.choices) == expected

    @pytest.mark.parametrize(
        "field, expected",
        (
            (EnumField(Colour), (("red", "Red"), ("green", "Green"), ("blue", "Blue"))),
            (
                EnumField(Number),
                ((13, "Thirteen"), (42, "FortyTwo"), (69, "SixtyNine")),
            ),
            (
                EnumField(Colour, choices=(Colour.Red, Colour.Blue)),
                (("red", "Red"), ("blue", "Blue")),
            ),
        ),
    )
    @pytest.mark.skipif("sys.version_info.major < 3")
    def test_choices_doc_text(self, field, expected):
        assert field.choices_doc_text == expected

    @pytest.mark.parametrize(
        "field, expected",
        (
            (EnumField(Colour), {("red", "Red"), ("green", "Green"), ("blue", "Blue")}),
            (
                EnumField(Number),
                {(13, "Thirteen"), (42, "FortyTwo"), (69, "SixtyNine")},
            ),
            (
                EnumField(Colour, choices=(Colour.Red, Colour.Blue)),
                {("red", "Red"), ("blue", "Blue")},
            ),
        ),
    )
    def test_choices_doc_text__with_sets(self, field, expected):
        """Use sets to handle random ordering in earlier Python releases"""
        assert set(field.choices_doc_text) == expected


class TestPathField:
    @pytest.mark.parametrize(
        "value, expected",
        (
            (None, None),
            ("abc", pathlib.Path("abc")),
            ("/this/is/the/true/path", pathlib.Path("/this/is/the/true/path")),
        ),
    )
    def test_to_python__valid(self, value, expected):
        field = odin.PathField()

        actual = field.to_python(value)

        assert actual == expected

    @pytest.mark.parametrize("value", (123,))
    def test_to_python__invalid(self, value):
        field = odin.PathField()

        with pytest.raises(ValidationError):
            field.to_python(value)

    @pytest.mark.parametrize(
        "value, expected",
        (
            (None, None),
            ("abc", None),
            (pathlib.Path("abc"), "abc"),
            (pathlib.Path("/this/is/the/true/path"), "/this/is/the/true/path"),
        ),
    )
    def test_prepare(self, value, expected):
        field = odin.PathField()

        actual = field.prepare(value)

        assert actual == expected


class TestRegexField:
    @pytest.mark.parametrize(
        "value, expected",
        (
            (None, None),
            ("simple[0-9](match)", re.compile("simple[0-9](match)")),
        ),
    )
    def test_to_python__valid(self, value, expected):
        field = odin.RegexField()

        actual = field.to_python(value)

        assert actual == expected

    @pytest.mark.parametrize("value", (123, "invalid[0-9(expression)"))
    def test_to_python__invalid(self, value):
        field = odin.RegexField()

        with pytest.raises(ValidationError):
            field.to_python(value)

    @pytest.mark.parametrize(
        "value, expected",
        (
            (None, None),
            ("simple[0-9](match)", None),
            (re.compile("simple[0-9](match)"), "simple[0-9](match)"),
        ),
    )
    def test_prepare(self, value, expected):
        field = odin.RegexField()

        actual = field.prepare(value)

        assert actual == expected
