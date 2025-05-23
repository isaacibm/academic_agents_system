from langchain.prompts import PromptTemplate, FewShotPromptTemplate

# Lista de exemplos few-shot
examples = [
    {
        "context": "A derivada da função f(x) = x² é 2x. A derivada mede a taxa de variação instantânea de uma função.",
        "question": "O que é derivada e qual a derivada de f(x) = x²?",
        "answer": "A derivada mede a taxa de variação instantânea de uma função. A derivada de f(x) = x² é 2x."
    },
    {
        "context": "O método de Newton é um algoritmo iterativo para encontrar raízes de funções. A fórmula é: xₙ₊₁ = xₙ - f(xₙ)/f'(xₙ).",
        "question": "Como funciona o método de Newton?",
        "answer": "O método de Newton é um algoritmo iterativo que calcula aproximações sucessivas para uma raiz de uma função. A fórmula é xₙ₊₁ = xₙ - f(xₙ)/f'(xₙ)."
    },
    {
        "context": "O determinante de uma matriz 2x2 com elementos a, b, c, d é dado por ad - bc. O determinante indica se a matriz é invertível.",
        "question": "Como calcular o determinante de uma matriz 2x2 e o que ele indica?",
        "answer": "O determinante de uma matriz 2x2 é ad - bc. Se o determinante for diferente de zero, a matriz é invertível."
    },
]

example_template = """
Documentos:
{context}
Pergunta:
{question}
Resposta:
{answer}
"""

example_prompt = PromptTemplate(
    input_variables=["context", "question", "answer"],
    template=example_template,
)

few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="Você é um assistente acadêmico especializado nas disciplinas de Cálculo, Álgebra Linear e Cálculo Numérico. Responda às perguntas utilizando APENAS as informações dos documentos fornecidos. Seja objetivo, claro e preciso.",
    suffix="""
Agora responda à pergunta:
Documentos:
{context}
Pergunta:
{question}
Resposta:""",
    input_variables=["context", "question"]
)
