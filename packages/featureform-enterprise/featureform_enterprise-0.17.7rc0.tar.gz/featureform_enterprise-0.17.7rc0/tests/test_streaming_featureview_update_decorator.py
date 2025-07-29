import sys
import pytest

sys.path.insert(0, "client/src/")
import featureform as ff
from test_client import s3_store, databricks_executor, MockStub


def update_feature(topic_a):
    """This should be the description"""
    return "SELECT * FROM {{topic_a}}"

def update_feature_no_params():
    return "SELECT * FROM {{topic_a}}"


def test_streaming_featureview_update_method():
    client = ff.Client(host="localhost:7878", insecure=True, dry_run=True)
    client._stub = MockStub()

    s3 = s3_store
    databricks_exec = databricks_executor
    spark = ff.register_spark(
        name="databricks",
        description="A Spark deployment we created for the Featureform quickstart",
        team="featureform-team",
        executor=databricks_exec,
        filestore=s3,
    )

    assert hasattr(spark, "sql_streaming_update")


@pytest.mark.parametrize(
    "feature_view,entity_column,timestamp_column,feature_mappings,inputs,fn,should_raise_on_init,init_error,should_raise_on_call,call_error",
    [
        (
            "fv_v1",
            "visitor_id",
            "ts",
            {"adp": ("adp", "var")},
            [ff.StreamInput(name="topic_a")],
            update_feature,
            False,
            "",
            False,
            "",
        ),
        (
            "fv_v1",
            "visitor_id",
            "ts",
            {},
            [ff.StreamInput(name="topic_a")],
            update_feature,
            False,
            "",
            True,
            "feature_mappings must be provided",
        ),
        (
            "fv_v1",
            "visitor_id",
            "ts",
            {"adp": ("adp", "var")},
            [],
            update_feature,
            False,
            "",
            True,
            "must have at least one topic input.",
        ),
        (
            "fv_v1",
            "visitor_id",
            "ts",
            {"adp": ("adp", "var")},
            [ff.StreamInput(name="topic_a"), ff.StreamInput(name="topic_b")],
            update_feature,
            False,
            "",
            True,
            "must have the same number of params as inputs.",
        ),
        (
            "fv_v1",
            "visitor_id",
            "ts",
            {"adp": ("adp", "var")},
            [ff.StreamInput(name="topic_a")],
            update_feature_no_params,
            False,
            "",
            True,
            "must have at least one topic param.",
        ),
    ],
)
def test_streaming_featureview_update_decorator(
    feature_view,
    entity_column,
    timestamp_column,
    feature_mappings,
    inputs,
    fn,
    should_raise_on_init,
    init_error,
    should_raise_on_call,
    call_error,
):
    if should_raise_on_init:
        with pytest.raises(ValueError) as e:
            streaming_update = ff.StreamingFeatureViewUpdateDecorator(
                registrar=ff.global_registrar,
                transformation_type=ff.TransformationType.SQL,
                feature_view=feature_view,
                entity_column=entity_column,
                timestamp_column=timestamp_column,
                provider="databricks",
                feature_mappings=feature_mappings,
                inputs=inputs,
            )
        assert init_error in str(e.value)
    else:
        streaming_update = ff.StreamingFeatureViewUpdateDecorator(
            registrar=ff.global_registrar,
            transformation_type=ff.TransformationType.SQL,
            feature_view=feature_view,
            entity_column=entity_column,
            timestamp_column=timestamp_column,
            provider="databricks",
            feature_mappings=feature_mappings,
            inputs=inputs,
        )

        if should_raise_on_call:
            with pytest.raises(ValueError) as e:
                streaming_update(fn)
            assert call_error in str(e.value)
        else:
            streaming_update(fn)
            assert streaming_update.name == fn.__name__
            assert streaming_update.description == fn.__doc__
            assert streaming_update.query == fn(*inputs)
            assert (
                streaming_update.owner == ff.global_registrar.must_get_default_owner()
            )
