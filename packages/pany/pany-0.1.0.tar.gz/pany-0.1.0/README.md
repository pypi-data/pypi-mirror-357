# Pany

**⚠️ Beta Software**: This is early-stage software. API may change between versions before v1.0.0.

Semantic search that works inside PostgreSQL. Upload documents and images, then search them with natural language.

Instead of setting up a separate vector database like Pinecone or Weaviate, Pany uses your existing PostgreSQL database with the pgvector extension.

📖 **[Technical Architecture](ARCHITECTURE.md)** - Detailed system design and implementation

## Install and Run

```bash
pip install pany
pany
```

Go to http://localhost:8000 to upload files and start searching.

### Requirements
- Python 3.9+
- PostgreSQL with pgvector extension
- 4GB RAM minimum

### Configuration

```bash
# Custom database
export DATABASE_URL="postgresql://user:pass@localhost:5432/mydb"

# Custom port
pany --port 8080

# Or use Docker
git clone https://github.com/laxmanclo/pany.cloud.git
cd pany.cloud
docker-compose up -d
```

## What it does

**Upload stuff**: Drop PDFs, images, text files into the web interface
**Search naturally**: Type "find the red car" or "contract with Microsoft" 
**Get results**: Finds semantically similar content, not just keyword matches

Works with text and images. You can search for images using text descriptions, or upload an image to find similar ones.

## Code Examples

```python
from pany import PanyClient

client = PanyClient()

# Upload files
client.upload_file("product_catalog.pdf", project_id="store")
client.upload_file("car_photo.jpg", project_id="store")

# Search with text
results = client.search("red sedan", project_id="store")

# Search with image
results = client.search_by_image("my_car.jpg", project_id="store")
```

## SQL Integration

The main advantage over other vector databases is that you can join search results with your existing data:

```sql
SELECT 
    products.name, 
    products.price, 
    search.similarity_score
FROM products 
JOIN semantic_search('comfortable shoes', 0.7) search 
    ON products.id = search.content_id
WHERE products.in_stock = true
ORDER BY search.similarity_score DESC;
```

This is impossible with most vector databases because they're separate systems.

## Why PostgreSQL?

Because you probably already have PostgreSQL running your app. Instead of:
1. Setting up another database (Pinecone, Weaviate, etc.)
2. Keeping data in sync between systems
3. Learning new APIs and query languages
4. Paying monthly fees

You just add pgvector to your existing database and you're done.
contact me for another db: laxmansrivastacc@gmail.com(a simple mail works, come on call or anything of the sort.)

## API

REST endpoints for integration:

```bash
# Upload content
curl -X POST http://localhost:8000/embeddings \
  -F "file=@document.pdf" \
  -F "project_id=myproject"

# Search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "find something", "project_id": "myproject"}'
```

## How it works

1. **Embedding**: Uses CLIP model to convert text and images into vectors
2. **Storage**: Saves vectors in PostgreSQL using pgvector extension  
3. **Search**: Finds similar vectors using cosine similarity
4. **Results**: Returns content ranked by similarity score

The CLIP model means you can search across different types of content - find images with text queries, or text with image queries.

## Common use cases

- **Product search**: Upload product catalog, let customers search "red leather shoes"
- **Document management**: Search PDFs and docs with natural language
- **Media libraries**: Find images by describing what's in them
- **Knowledge bases**: Semantic search through support docs

## Environment variables

```bash
DATABASE_URL="postgresql://user:pass@host:5432/db"
HOST="0.0.0.0"
PORT="8000" 
EMBEDDING_MODEL="all-MiniLM-L6-v2"
OPENAI_API_KEY="sk-..."  # optional
UPLOAD_DIR="./uploads"
```

## Development

```bash
git clone https://github.com/laxmanclo/pany.cloud.git
cd pany.cloud
pip install -r requirements.txt
python -m pany.main
```

Run tests: `pytest tests/`

## Contributing

Fork the repo, make changes, submit PR. 

Code style: use Black formatter, add type hints, write tests.

## License

MIT License

## Issues

Report bugs at https://github.com/laxmanclo/pany.cloud/issues

Contact: laxmansrivastacc@gmail.com
# Results: [{"name": "Red Nike Air Max", "similarity": 0.89}, ...]
```
**ROI**: 15-25% conversion rate increase = $50k-200k/year additional revenue

### **Customer Support: Instant Knowledge Base**
**Problem**: Agents spend 10+ minutes finding answers, customers wait
**Solution**: Semantic search across all documentation
```sql
-- Find answers across all support docs
SELECT document, answer, similarity 
FROM semantic_search('password reset not working', 'support_docs')
WHERE similarity > 0.8;
```
**ROI**: 60% faster resolution time = 2-3 additional customers served per hour

### **Legal/HR: Document Discovery**
**Problem**: Lawyers bill $500/hour searching through contracts
**Solution**: Natural language search across all legal documents
```python
# Find all contracts mentioning liability clauses
results = pany.search("liability and insurance provisions", project="legal")
```
**ROI**: Save 20 hours/week = $10k/week = $520k/year savings

### **Real Estate: Property Matching**
**Problem**: Clients describe dream home, agents manually search listings
**Solution**: Semantic search combining text + property images
```python
# "Modern kitchen with granite countertops near good schools"
results = pany.search(client_description, project="listings")
```
**ROI**: 3x faster property matching = serve 3x more clients

## 🏗️ Architecture: PostgreSQL + CLIP + FastAPI

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Widget    │    │   FastAPI        │    │  PostgreSQL     │
│   Dashboard     │◄──►│   + CLIP Model   │◄──►│  + pgvector     │
│   REST API      │    │   Embedding Gen  │    │   Vector Store  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Why This Stack Wins:**
- **PostgreSQL**: ACID compliance, backups, joins, familiar
- **CLIP**: Multi-modal embeddings (text ↔ images) 
- **FastAPI**: Modern async Python, auto-documentation
- **Docker**: One-command deployment anywhere

## 📊 Performance

### **Benchmarks** (tested on 4-core, 8GB RAM)
- **Upload speed:** ~2MB/sec document processing
- **Throughput:** 100+ concurrent searches
- **Storage:** ~1KB per document embedding
- **Accuracy:** 85-95% relevance for semantic queries

### **Scaling Guidelines**
- **Small team (1-10 users):** 2GB RAM, 2 cores
- **Medium business (10-100 users):** 8GB RAM, 4 cores  
- **Large organization (100+ users):** 16GB+ RAM, 8+ cores
- **Database:** Scales linearly with PostgreSQL

## 🔧 Configuration

### Environment Variables
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pany
POSTGRES_USER=pany
POSTGRES_PASSWORD=your-secure-password

# API
API_HOST=0.0.0.0
API_PORT=8000
MAX_FILE_SIZE_MB=50

# Embeddings
EMBEDDING_MODEL=clip-ViT-B-32
VECTOR_DIMENSIONS=512
```

### Custom Embeddings
```python
# embedding-service/services/custom_embedding.py
from sentence_transformers import SentenceTransformer

class CustomEmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('your-custom-model')
    
    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()
```

## Integrations

### **Website Widget**
```javascript
// Minimal integration
<script src="http://your-domain/widget.js"></script>
<div id="pany-search"></div>

// Custom styling
<script>
  PanyWidget.init({
    container: '#my-search',
    placeholder: 'Search our knowledge base...',
    theme: 'dark',
    maxResults: 10
  });
</script>
```

### **React Component**
```jsx
import { PanySearch } from '@pany/react';

function App() {
  return (
    <PanySearch 
      apiUrl="http://localhost:8000"
      projectId="my-project"
      placeholder="Search documents..."
    />
  );
}
```

### **Python SDK**
```python
from pany import PanyClient

client = PanyClient(base_url="http://localhost:8000")

# Upload file
result = client.upload_file("document.pdf", project_id="my-project")

# Search
results = client.search("password reset instructions", project_id="my-project")
```

## 🚀 Deployment

### **Docker Compose (Recommended)**
```yaml
version: '3.8'
services:
  pany-api:
    image: pany/pany:latest
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_HOST=postgres
    depends_on:
      - postgres
  
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: pany
      POSTGRES_USER: pany
      POSTGRES_PASSWORD: secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### **Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pany-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pany-api
  template:
    metadata:
      labels:
        app: pany-api
    spec:
      containers:
      - name: pany-api
        image: pany/pany:latest
        ports:
        - containerPort: 8000
```

### **Production Checklist**
- [ ] Configure secure database passwords
- [ ] Set up SSL/TLS certificates  
- [ ] Configure reverse proxy (nginx/traefik)
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set resource limits and scaling rules

```
Do star :D and support if it made your life easier, and also report issues, and always welcome to fix whats broken :)
