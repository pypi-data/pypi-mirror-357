import odin
from odin.codecs import json_codec
from odin.contrib.money import Amount, AmountField


class AmountResource(odin.Resource):
    class Meta:
        namespace = "odin.tests"

    a = AmountField(null=True)
    b = AmountField()
    c = AmountField()


class TestMoneySerialisation:
    def test_serialise(self):
        resource = AmountResource(a=None, b=Amount(10), c=Amount(22.02, "AUD"))

        actual = json_codec.dumps(resource, sort_keys=True)

        assert (
            actual
            == '{"$": "odin.tests.AmountResource", "a": null, "b": [10.0, "XXX"], "c": [22.02, "AUD"]}'
        )

    def test_deserialise(self):
        resource = json_codec.loads(
            '{"$": "odin.tests.AmountResource", "a": null, "b": 10, "c": [23.66, "AUD"]}'
        )

        assert None is resource.a
        assert Amount(10) == resource.b
        assert Amount(23.66, "AUD") == resource.c
