from crewai import Agent, Task, Process, Crew, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource


pdf_tool = PDFKnowledgeSource(
    file_path=['calc4.pdf', 'SMA_88_apostila_algebra_linear.pdf', 
               'SMA_88_Calculo2Vetorial.pdf', 'SMA_88_claudio.pdf']
)

llm = LLM(model="watsonx/meta-llama/llama-3-1-70b-instruct", temperature=0)


@CrewBase
class ComplianceCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/task.yaml"

    @agent
    def especialista_compliance(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_compliance"],
            verbose=True,
            tools=[],
            llm=llm,
        )
      
    @task
    def responder_pergunta_compliance(self) -> Task:
        return Task(
            config=self.tasks_config["responder_pergunta_compliance"],
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MQuestKnowledge crew"""

        return Crew(
            agents=[self.especialista_compliance()],
            tasks=[self.responder_pergunta_compliance()],
            process=Process.sequential,
            verbose=True,
            knowledge_sources=[pdf_tool]
        )