from app.simulation.causal import Mechanism,Mode,Status,simulate
def test_unknown_model_assumption_becomes_indeterminate():
    result=simulate({"A","B"},[Mechanism("m",("A",),"B",Mode.ALL,"model_assumption")],{"A"})
    assert result.statuses["B"] is Status.INDETERMINATE
def test_multiple_interventions_are_deterministic():
    mechanisms=[Mechanism("m",("A","B"),"C",Mode.ALL)]
    assert simulate({"A","B","C"},mechanisms,{"A","B"})==simulate({"A","B","C"},mechanisms,{"B","A"})
