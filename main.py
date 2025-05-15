from crew import ComplianceCrew


def run_compliance_assistant(pergunta: str):

    print("Instanciando ComplienceCrew...")
    crew_instance = ComplianceCrew()

    print("Rodando kickoff...")
    result = crew_instance.crew().kickoff(inputs={"pergunta": pergunta})

    return result