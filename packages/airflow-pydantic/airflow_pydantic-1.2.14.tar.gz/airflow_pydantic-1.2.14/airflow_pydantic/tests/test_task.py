from airflow_pydantic import Task, TaskArgs


class TestTask:
    def test_task_args(self, task_args):
        t = task_args

        # Test roundtrips
        assert t == TaskArgs.model_validate(t.model_dump(exclude_unset=True))
        assert t == TaskArgs.model_validate_json(t.model_dump_json(exclude_unset=True))

    def test_task(self):
        t = Task(
            task_id="a-task",
            operator="airflow.operators.empty.EmptyOperator",
            dependencies=[],
            args=None,
        )

        # Test roundtrips
        assert t == Task.model_validate(t.model_dump(exclude_unset=True))
        assert t == Task.model_validate_json(t.model_dump_json(exclude_unset=True))
