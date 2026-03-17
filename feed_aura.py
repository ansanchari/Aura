from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

print("Waking up the database...")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
client = QdrantClient(path="./qdrant_aura_db")

vector_store = QdrantVectorStore(
    client=client,
    collection_name="womens_health_knowledge",
    embedding=embeddings,
)

print("Injecting medical documents...")

medical_data = [
    Document(page_content="Polycystic ovary syndrome (PCOS) is a common hormonal disorder among women of reproductive age. The most common metabolic markers of PCOS include severe insulin resistance, elevated fasting glucose, high levels of luteinizing hormone (LH), and elevated circulating androgens (hyperandrogenism)."),
    Document(page_content="Endometriosis is a painful condition where tissue similar to the lining of the uterus grows outside the uterus. Common diagnostic markers are not easily found in blood tests, but treatments often involve hormonal contraceptives, GnRH agonists, and laparoscopic excision surgery."),
    Document(page_content="The menstrual cycle consists of four distinct phases: menstruation, the follicular phase, ovulation, and the luteal phase. During the luteal phase, progesterone peaks, which can lead to increased resting metabolic rate, higher energy expenditure, and feelings of physical fatigue.")
]

vector_store.add_documents(medical_data)

print("Success! Aura now has medical data in her brain.")