import uuid
from sqlalchemy.orm import Session
from app.models.models import (
    User, StudentProfile, Skill, StudentSkill, Role, RoleSkill,
    StudentProject, StudentCertification, StudentExperience,
    LearningResource, Question
)

CANONICAL_ROLES = [
    {
        "id": "b0000001-0000-0000-0000-000000000001",
        "slug": "software-developer",
        "title": "Software Developer",
        "category": "Software Engineering",
        "description": "Designs, codes, tests, and maintains core software applications, algorithms, and system integrations using modern programming paradigms.",
        "academic_requirements": "B.Tech/B.E/BCA/MCA in Computer Science, IT, or related engineering discipline.",
        "career_outlook": "High sustained industry demand across IT product firms, startups, and enterprise services.",
        "skills": [
            ("Data Structures & Algorithms", "required", "Advanced", 1.8),
            ("Java", "required", "Intermediate", 1.5),
            ("Python", "preferred", "Intermediate", 1.2),
            ("SQL", "required", "Intermediate", 1.3),
            ("Git & GitHub", "required", "Intermediate", 1.0),
            ("System Design", "preferred", "Intermediate", 1.2),
            ("Unit Testing & TDD", "preferred", "Beginner", 1.0)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000000002",
        "slug": "frontend-developer",
        "title": "Frontend Developer",
        "category": "Web Development",
        "description": "Specializes in client-side web engineering, responsive user interfaces, reactive component architectures, and web performance optimization.",
        "academic_requirements": "B.Tech/B.E/BCA/MCA or relevant computer science background with strong portfolio.",
        "career_outlook": "Exceptional demand for modern frontend engineers proficient in React, Next.js, and TypeScript.",
        "skills": [
            ("JavaScript", "required", "Advanced", 1.8),
            ("TypeScript", "required", "Intermediate", 1.5),
            ("React", "required", "Advanced", 1.8),
            ("Next.js", "required", "Intermediate", 1.4),
            ("HTML5/CSS3", "required", "Advanced", 1.5),
            ("Tailwind CSS", "preferred", "Intermediate", 1.2),
            ("Git & GitHub", "required", "Intermediate", 1.0),
            ("REST APIs", "preferred", "Intermediate", 1.1)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000000003",
        "slug": "backend-developer",
        "title": "Backend Developer",
        "category": "Software Engineering",
        "description": "Architects server-side logic, high-throughput microservices, RESTful and GraphQL APIs, relational database queries, and caching mechanisms.",
        "academic_requirements": "B.Tech/B.E in Computer Science, Software Engineering, or Information Technology.",
        "career_outlook": "Critical role in cloud infrastructure, enterprise SaaS, and distributed systems architecture.",
        "skills": [
            ("Python", "required", "Advanced", 1.7),
            ("FastAPI", "required", "Intermediate", 1.5),
            ("SQL", "required", "Advanced", 1.6),
            ("PostgreSQL", "required", "Intermediate", 1.4),
            ("Docker", "preferred", "Intermediate", 1.3),
            ("Redis", "preferred", "Intermediate", 1.2),
            ("REST APIs", "required", "Advanced", 1.6),
            ("Git & GitHub", "required", "Intermediate", 1.0),
            ("System Design", "preferred", "Intermediate", 1.3)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000000004",
        "slug": "fullstack-developer",
        "title": "Full-Stack Developer",
        "category": "Software Engineering",
        "description": "Bridges end-to-end software delivery, mastering frontend reactive UI, backend microservice APIs, and relational/document persistence.",
        "academic_requirements": "B.Tech/B.E in Computer Science or Information Technology.",
        "career_outlook": "Strong hiring preference in agile startups and fast-growing product companies.",
        "skills": [
            ("JavaScript", "required", "Advanced", 1.6),
            ("TypeScript", "preferred", "Intermediate", 1.3),
            ("React", "required", "Advanced", 1.6),
            ("Node.js", "required", "Intermediate", 1.5),
            ("Express.js", "preferred", "Intermediate", 1.3),
            ("PostgreSQL", "required", "Intermediate", 1.4),
            ("Docker", "preferred", "Beginner", 1.1),
            ("Git & GitHub", "required", "Intermediate", 1.0),
            ("REST APIs", "required", "Advanced", 1.5)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000000005",
        "slug": "data-analyst",
        "title": "Data Analyst",
        "category": "Data & Analytics",
        "description": "Cleans, transforms, analyzes, and visualizes complex enterprise data to discover trends and deliver actionable business intelligence.",
        "academic_requirements": "Degree in Computer Science, Statistics, Mathematics, Economics, or Data Science.",
        "career_outlook": "Ubiquitous demand across financial services, e-commerce, consulting, and tech enterprises.",
        "skills": [
            ("SQL", "required", "Advanced", 1.9),
            ("Python", "required", "Intermediate", 1.5),
            ("Pandas & NumPy", "required", "Intermediate", 1.6),
            ("Data Visualization", "required", "Advanced", 1.7),
            ("Statistics & Probability", "required", "Intermediate", 1.5),
            ("Git & GitHub", "optional", "Beginner", 0.8)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000000006",
        "slug": "data-scientist",
        "title": "Data Scientist",
        "category": "Data Science & AI",
        "description": "Applies rigorous statistical modeling, feature engineering, and predictive machine learning to solve ambiguous business challenges.",
        "academic_requirements": "Degree in Computer Science, Data Science, Statistics, or Applied Mathematics.",
        "career_outlook": "Elite compensation and strategic influence in data-mature organizations.",
        "skills": [
            ("Python", "required", "Advanced", 1.8),
            ("Machine Learning", "required", "Advanced", 1.8),
            ("Statistics & Probability", "required", "Advanced", 1.7),
            ("Pandas & NumPy", "required", "Advanced", 1.6),
            ("SQL", "required", "Intermediate", 1.4),
            ("Data Visualization", "preferred", "Intermediate", 1.2),
            ("Deep Learning", "preferred", "Intermediate", 1.3)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000000007",
        "slug": "ml-engineer",
        "title": "Machine Learning Engineer",
        "category": "Artificial Intelligence",
        "description": "Productionizes ML models, designing training workflows, inference endpoints, low-latency model serving, and feature stores.",
        "academic_requirements": "B.Tech/M.Tech in Computer Science, AI, or Data Engineering.",
        "career_outlook": "One of the most competitive and highest-paying software disciplines worldwide.",
        "skills": [
            ("Python", "required", "Advanced", 1.8),
            ("Machine Learning", "required", "Advanced", 1.8),
            ("Deep Learning", "required", "Intermediate", 1.6),
            ("Docker", "required", "Intermediate", 1.4),
            ("FastAPI", "preferred", "Intermediate", 1.3),
            ("Natural Language Processing", "preferred", "Intermediate", 1.4),
            ("Git & GitHub", "required", "Intermediate", 1.0),
            ("Data Structures & Algorithms", "preferred", "Intermediate", 1.2)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000000008",
        "slug": "devops-engineer",
        "title": "DevOps Engineer",
        "category": "Infrastructure & Cloud",
        "description": "Automates software build cycles, manages continuous integration and continuous deployment (CI/CD), containers, and site reliability.",
        "academic_requirements": "Computer Science, IT, or Networking Engineering degree.",
        "career_outlook": "Vital role ensuring high availability and developer productivity across tech teams.",
        "skills": [
            ("Linux & Bash", "required", "Advanced", 1.8),
            ("Docker", "required", "Advanced", 1.8),
            ("CI/CD Pipelines", "required", "Advanced", 1.7),
            ("AWS", "required", "Intermediate", 1.6),
            ("Kubernetes", "preferred", "Intermediate", 1.5),
            ("Git & GitHub", "required", "Intermediate", 1.3),
            ("Python", "preferred", "Intermediate", 1.1)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000000009",
        "slug": "cloud-engineer",
        "title": "Cloud Engineer",
        "category": "Cloud Infrastructure",
        "description": "Deploys, monitors, and optimizes scalable cloud infrastructure, managing networks, IAM access controls, security, and cloud cost efficiency.",
        "academic_requirements": "Engineering degree in Computer Science, Information Technology, or Electronics.",
        "career_outlook": "Massive ongoing transition to cloud-first workloads across all industries.",
        "skills": [
            ("AWS", "required", "Advanced", 1.9),
            ("Linux & Bash", "required", "Intermediate", 1.5),
            ("Docker", "required", "Intermediate", 1.5),
            ("CI/CD Pipelines", "preferred", "Intermediate", 1.3),
            ("Network Security", "preferred", "Intermediate", 1.3),
            ("Python", "optional", "Beginner", 1.0)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000001010",
        "slug": "cybersecurity-analyst",
        "title": "Cybersecurity Analyst",
        "category": "Security",
        "description": "Defends enterprise systems and intellectual property by auditing network traffic, hardening security postures, and mitigating threats.",
        "academic_requirements": "Degree in Cybersecurity, Computer Science, or Information Technology.",
        "career_outlook": "Critical global shortage of cybersecurity personnel; high job security.",
        "skills": [
            ("Network Security", "required", "Advanced", 1.9),
            ("Cryptography", "required", "Intermediate", 1.6),
            ("Linux & Bash", "required", "Intermediate", 1.5),
            ("Python", "preferred", "Intermediate", 1.3),
            ("SQL", "preferred", "Beginner", 1.0)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000001011",
        "slug": "qa-engineer",
        "title": "QA / Test Engineer",
        "category": "Quality Assurance",
        "description": "Architects end-to-end automated testing suites, regression pipelines, and performance stress tests to guarantee defect-free software.",
        "academic_requirements": "B.Tech/B.E in Computer Science or Information Technology.",
        "career_outlook": "Strong need for test automation engineers skilled in Selenium, Playwright, and Python/Java.",
        "skills": [
            ("Unit Testing & TDD", "required", "Advanced", 1.8),
            ("Selenium & Playwright", "required", "Advanced", 1.8),
            ("Python", "required", "Intermediate", 1.4),
            ("SQL", "preferred", "Intermediate", 1.2),
            ("CI/CD Pipelines", "preferred", "Intermediate", 1.3),
            ("Git & GitHub", "required", "Intermediate", 1.0)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000001012",
        "slug": "business-analyst",
        "title": "Business Analyst",
        "category": "Product & Analytics",
        "description": "Acts as the bridge between business stakeholders and engineering teams, gathering requirements and translating them into user stories.",
        "academic_requirements": "B.Tech, MBA, BCA/MCA, or relevant multidisciplinary analytical degree.",
        "career_outlook": "High corporate demand across IT consulting, banking, and SaaS products.",
        "skills": [
            ("SQL", "required", "Intermediate", 1.6),
            ("Data Visualization", "required", "Advanced", 1.7),
            ("Agile & Scrum", "required", "Advanced", 1.7),
            ("Data Structures & Algorithms", "optional", "Beginner", 0.7)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000001013",
        "slug": "database-administrator",
        "title": "Database Administrator",
        "category": "Database Engineering",
        "description": "Ensures uninterrupted database uptime, index performance tuning, replication, backup procedures, security, and schema migration integrity.",
        "academic_requirements": "Computer Science or Information Technology degree.",
        "career_outlook": "Essential in large-scale banking, telecom, healthcare, and enterprise ERP environments.",
        "skills": [
            ("SQL", "required", "Advanced", 2.0),
            ("PostgreSQL", "required", "Advanced", 1.9),
            ("Redis", "preferred", "Intermediate", 1.4),
            ("Linux & Bash", "required", "Intermediate", 1.5),
            ("System Design", "preferred", "Intermediate", 1.3)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000001014",
        "slug": "ui-ux-designer",
        "title": "UI/UX Designer",
        "category": "Design & UX",
        "description": "Conducts user research, creates high-fidelity wireframes and interactive prototypes, and maintains component-driven design systems.",
        "academic_requirements": "Degree in Design, Human-Computer Interaction, CS, or multimedia.",
        "career_outlook": "High value placed on product designers who understand responsive web and SaaS heuristics.",
        "skills": [
            ("Figma & UI Design", "required", "Advanced", 2.0),
            ("HTML5/CSS3", "preferred", "Intermediate", 1.4),
            ("Agile & Scrum", "preferred", "Intermediate", 1.2)
        ]
    },
    {
        "id": "b0000001-0000-0000-0000-000000001015",
        "slug": "systems-engineer",
        "title": "Technical Support / Systems Engineer",
        "category": "IT Operations",
        "description": "Administers enterprise servers, operating system environments, network routing, and workstation infrastructure with proactive troubleshooting.",
        "academic_requirements": "Degree or Diploma in CS, IT, Electronics, or Computer Applications.",
        "career_outlook": "Consistent baseline recruitment during college campus placement drives.",
        "skills": [
            ("Linux & Bash", "required", "Advanced", 1.8),
            ("Network Security", "required", "Intermediate", 1.6),
            ("Python", "preferred", "Beginner", 1.2),
            ("SQL", "preferred", "Beginner", 1.0)
        ]
    }
]

CANONICAL_SKILLS = [
    ("Python", "Programming", ["python3", "py", "python-3"], "High-level programming language used in backend, scripting, and data science."),
    ("JavaScript", "Programming", ["js", "es6", "ecmascript"], "Core scripting language of the web for client and server side."),
    ("TypeScript", "Programming", ["ts"], "Typed superset of JavaScript providing compile-time safety."),
    ("Java", "Programming", ["java8", "java11", "java17", "core java"], "Object-oriented language popular for enterprise systems and Android."),
    ("C++", "Programming", ["cpp", "c plus plus"], "High-performance language used in systems programming and DSA."),
    ("SQL", "Database", ["mysql", "relational db", "sql queries"], "Standard language for querying and managing relational databases."),
    ("PostgreSQL", "Database", ["postgres", "psql"], "Advanced open-source object-relational database system."),
    ("MongoDB", "Database", ["mongo", "nosql"], "Document-oriented NoSQL database for flexible JSON schemas."),
    ("Redis", "Database", ["caching", "in-memory db"], "In-memory data structure store used as a cache and message broker."),
    ("React", "Frontend", ["reactjs", "react.js"], "Component-based declarative library for user interfaces."),
    ("Next.js", "Frontend", ["nextjs", "next"], "Production React framework with App Router, SSR, and API routes."),
    ("HTML5/CSS3", "Frontend", ["html", "css", "responsive design"], "Core web markup and style standards."),
    ("Tailwind CSS", "Frontend", ["tailwind", "tailwindcss"], "Utility-first CSS framework for rapid modern UI development."),
    ("FastAPI", "Backend", ["fast-api"], "Modern, high-performance web framework for Python APIs."),
    ("Node.js", "Backend", ["nodejs", "node"], "JavaScript runtime built on Chrome V8 engine."),
    ("Express.js", "Backend", ["express", "expressjs"], "Minimalist web framework for Node.js REST APIs."),
    ("Django", "Backend", ["django-rest-framework", "drf"], "Full-featured batteries-included Python framework."),
    ("REST APIs", "Backend", ["api design", "restful", "http apis"], "Architectural style for web services using HTTP verbs."),
    ("Data Structures & Algorithms", "Programming", ["dsa", "algorithms", "data structures", "leetcode"], "Core CS foundation covering arrays, trees, graphs, and dynamic programming."),
    ("Git & GitHub", "DevOps & Cloud", ["git", "github", "version control"], "Distributed version control system and collaborative hosting."),
    ("Docker", "DevOps & Cloud", ["containerization", "containers", "docker-compose"], "Platform for containerizing applications."),
    ("Kubernetes", "DevOps & Cloud", ["k8s"], "Automated container orchestration and scaling platform."),
    ("AWS", "DevOps & Cloud", ["amazon web services", "ec2", "s3", "lambda"], "Cloud infrastructure platform provided by Amazon."),
    ("CI/CD Pipelines", "DevOps & Cloud", ["continuous integration", "github actions", "jenkins", "ci cd"], "Automated builds, testing, and continuous delivery workflows."),
    ("Linux & Bash", "DevOps & Cloud", ["linux", "bash", "shell scripting", "unix"], "Operating system environment and command-line shell scripts."),
    ("Machine Learning", "Data & AI", ["ml", "scikit-learn", "supervised learning"], "Statistical methods enabling models to learn from historical data."),
    ("Deep Learning", "Data & AI", ["neural networks", "pytorch", "tensorflow"], "Neural network architectures for high-dimensional representation learning."),
    ("Natural Language Processing", "Data & AI", ["nlp", "transformers", "bert", "llm"], "Techniques for analyzing and processing natural human language."),
    ("Pandas & NumPy", "Data & AI", ["pandas", "numpy", "data wrangling"], "Python libraries for array calculation and data manipulation."),
    ("Data Visualization", "Data & AI", ["tableau", "power bi", "matplotlib", "seaborn"], "Conveying insights through visual charts and dashboards."),
    ("Statistics & Probability", "Data & AI", ["statistics", "inferential statistics", "probability"], "Mathematical theory for inference and hypothesis testing."),
    ("Unit Testing & TDD", "Testing", ["pytest", "jest", "unit tests", "testing"], "Writing automated test cases to verify code behavior."),
    ("Selenium & Playwright", "Testing", ["selenium", "playwright", "e2e testing", "automation testing"], "Browser automation frameworks for end-to-end validation."),
    ("Network Security", "Security", ["cybersecurity", "firewalls", "tcp/ip", "wireshark"], "Protocols and defenses protecting computer networks."),
    ("Cryptography", "Security", ["encryption", "tls", "ssl", "public key"], "Securing communication and storage via encryption algorithms."),
    ("Figma & UI Design", "Design & UX", ["figma", "wireframing", "prototyping", "ui ux"], "Interface design tool for high-fidelity interactive wireframes."),
    ("System Design", "Software Engineering", ["high level design", "scalability", "distributed systems"], "Designing large-scale software systems and architectures."),
    ("Agile & Scrum", "Soft Skills", ["agile", "scrum", "sprint", "jira"], "Iterative project delivery framework emphasizing collaboration.")
]

CURATED_RESOURCES = [
    {
        "title": "Python Official Documentation & Tutorial",
        "skill_name": "Python",
        "difficulty": "Beginner",
        "resource_type": "Documentation",
        "url": "https://docs.python.org/3/tutorial/",
        "estimated_hours": 6,
        "rating": 4.9
    },
    {
        "title": "FastAPI Web Framework Complete Guide",
        "skill_name": "FastAPI",
        "difficulty": "Intermediate",
        "resource_type": "Course",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "estimated_hours": 8,
        "rating": 4.8
    },
    {
        "title": "React Official Documentation & Interactive Guide",
        "skill_name": "React",
        "difficulty": "Intermediate",
        "resource_type": "Documentation",
        "url": "https://react.dev/learn",
        "estimated_hours": 10,
        "rating": 4.9
    },
    {
        "title": "Next.js App Router Masterclass",
        "skill_name": "Next.js",
        "difficulty": "Intermediate",
        "resource_type": "Tutorial",
        "url": "https://nextjs.org/docs/app",
        "estimated_hours": 8,
        "rating": 4.8
    },
    {
        "title": "PostgreSQL Tutorial & Query Optimization",
        "skill_name": "PostgreSQL",
        "difficulty": "Intermediate",
        "resource_type": "Course",
        "url": "https://www.postgresqltutorial.com/",
        "estimated_hours": 7,
        "rating": 4.7
    },
    {
        "title": "Docker for Developers — Container Fundamentals",
        "skill_name": "Docker",
        "difficulty": "Beginner",
        "resource_type": "Tutorial",
        "url": "https://docker-curriculum.com/",
        "estimated_hours": 5,
        "rating": 4.8
    },
    {
        "title": "Data Structures & Algorithms in Python",
        "skill_name": "Data Structures & Algorithms",
        "difficulty": "Intermediate",
        "resource_type": "Practice",
        "url": "https://neetcode.io/roadmap",
        "estimated_hours": 20,
        "rating": 4.9
    },
    {
        "title": "Machine Learning with Scikit-Learn & Python",
        "skill_name": "Machine Learning",
        "difficulty": "Intermediate",
        "resource_type": "Course",
        "url": "https://scikit-learn.org/stable/tutorial/index.html",
        "estimated_hours": 12,
        "rating": 4.7
    },
    {
        "title": "Linux Command Line & Bash Scripting",
        "skill_name": "Linux & Bash",
        "difficulty": "Beginner",
        "resource_type": "Tutorial",
        "url": "https://linuxjourney.com/",
        "estimated_hours": 6,
        "rating": 4.8
    },
    {
        "title": "Figma Masterclass for UI/UX Design",
        "skill_name": "Figma & UI Design",
        "difficulty": "Beginner",
        "resource_type": "Video",
        "url": "https://help.figma.com/hc/en-us/categories/360002051613-Get-started",
        "estimated_hours": 6,
        "rating": 4.7
    }
]

CURATED_QUESTIONS = [
    # Aptitude - Quantitative
    {
        "category": "Aptitude",
        "sub_category": "Quantitative",
        "difficulty": "Easy",
        "question_text": "A train running at 54 km/hr crosses a platform in 20 seconds. If the length of the platform is 120 meters, what is the length of the train?",
        "options": ["180 meters", "200 meters", "150 meters", "220 meters"],
        "correct_answer": "180 meters",
        "explanation": "Speed = 54 * (5/18) = 15 m/s. Total distance in 20 sec = 15 * 20 = 300 m. Train length = 300 - 120 = 180 meters."
    },
    {
        "category": "Aptitude",
        "sub_category": "Logical",
        "difficulty": "Intermediate",
        "question_text": "In a certain code, 'PYTHON' is written as 'QZWILM'. How is 'CODING' written in that code?",
        "options": ["DPEJOH", "DPCHMH", "DPDHOH", "BPCHMF"],
        "correct_answer": "DPEJOH",
        "explanation": "Each letter is shifted: P->Q (+1), Y->Z (+1), T->W (+3) ... Following the progressive pattern, C+1=D, O+1=P, D+1=E, I+1=J, N+1=O, G+1=H -> DPEJOH."
    },
    {
        "category": "Aptitude",
        "sub_category": "Verbal",
        "difficulty": "Easy",
        "question_text": "Identify the word most opposite in meaning to 'METICULOUS':",
        "options": ["Careless", "Thorough", "Detailed", "Diligent"],
        "correct_answer": "Careless",
        "explanation": "Meticulous means showing great attention to detail. Careless is its direct antonym."
    },
    # Technical - Python / Backend
    {
        "category": "Technical",
        "sub_category": "Backend Development",
        "difficulty": "Intermediate",
        "question_text": "What is the difference between synchronous and asynchronous route handlers in FastAPI?",
        "options": [
            "Async handlers run in an event loop using coroutines, whereas standard def handlers run in an external threadpool",
            "Async handlers only work with SQLite databases",
            "Sync handlers are always 10x faster for I/O operations",
            "There is no operational difference"
        ],
        "correct_answer": "Async handlers run in an event loop using coroutines, whereas standard def handlers run in an external threadpool",
        "explanation": "FastAPI runs async def handlers directly on the ASGI event loop (ideal for non-blocking I/O). Regular def handlers are executed in a threadpool to avoid blocking the event loop."
    },
    {
        "category": "Technical",
        "sub_category": "Data Structures",
        "difficulty": "Intermediate",
        "question_text": "What is the worst-case and average-case time complexity of searching an element in a balanced Binary Search Tree (AVL / Red-Black)?",
        "options": ["O(1) average, O(N) worst", "O(log N) average, O(log N) worst", "O(N) average, O(N log N) worst", "O(log N) average, O(N) worst"],
        "correct_answer": "O(log N) average, O(log N) worst",
        "explanation": "Because self-balancing trees maintain a height of O(log N), both average and worst case search operations are strictly bounded to O(log N)."
    },
    {
        "category": "Technical",
        "sub_category": "Databases",
        "difficulty": "Intermediate",
        "question_text": "In relational databases, what does the ACID property 'Isolation' guarantee?",
        "options": [
            "Data is replicated across multiple servers",
            "Concurrent transactions execute without interfering with one another, producing results identical to serial execution",
            "Database transactions never write to disk until committed",
            "All foreign key constraints are enforced instantaneously"
        ],
        "correct_answer": "Concurrent transactions execute without interfering with one another, producing results identical to serial execution",
        "explanation": "Isolation guarantees that multiple concurrent transactions cannot witness uncommitted or contradictory intermediate states."
    },
    # HR / Behavioral
    {
        "category": "HR",
        "sub_category": "Behavioral",
        "difficulty": "Intermediate",
        "question_text": "Tell me about a time you encountered a conflict or disagreement within a technical project team. How did you resolve it?",
        "options": None,
        "correct_answer": "STAR Format Approach",
        "explanation": "Use the Situation-Task-Action-Result format: objectively state the technical debate (e.g. choice of database), focus on data-driven benchmarks and trade-off analysis, show active listening, and conclude with the successful collaborative outcome."
    },
    {
        "category": "HR",
        "sub_category": "Introduction",
        "difficulty": "Easy",
        "question_text": "Walk me through your resume and why you are interested in this specific role.",
        "options": None,
        "correct_answer": "Structured Career Narrative",
        "explanation": "Deliver a 90-second pitch: 1) Educational background and core technical passion, 2) Key academic/internship project that solidified your interest, 3) Targeted alignment between your skills and the company's tech stack."
    }
]

def seed_database_if_empty(db: Session):
    """
    Checks if roles exist in the database. If not, seeds all roles, canonical skills,
    knowledge graph mappings, learning resources, questions, and a sample student profile.
    """
    existing_roles_count = db.query(Role).count()
    if existing_roles_count > 0:
        return

    # 1. Seed Skills
    skill_map = {}
    for name, cat, aliases, desc in CANONICAL_SKILLS:
        skill = Skill(
            name=name,
            category=cat,
            aliases=aliases,
            description=desc
        )
        db.add(skill)
        db.flush()
        skill_map[name] = skill

    # 2. Seed Roles and Role-Skill Mappings
    role_map = {}
    for r_data in CANONICAL_ROLES:
        role = Role(
            id=r_data["id"],
            slug=r_data["slug"],
            title=r_data["title"],
            category=r_data["category"],
            description=r_data["description"],
            academic_requirements=r_data["academic_requirements"],
            career_outlook=r_data["career_outlook"]
        )
        db.add(role)
        db.flush()
        role_map[r_data["title"]] = role

        for skill_name, imp, min_prof, weight in r_data["skills"]:
            if skill_name in skill_map:
                role_skill = RoleSkill(
                    role_id=role.id,
                    skill_id=skill_map[skill_name].id,
                    importance=imp,
                    minimum_proficiency=min_prof,
                    weight=weight
                )
                db.add(role_skill)

    # 3. Seed Learning Resources
    for res in CURATED_RESOURCES:
        sk_id = skill_map[res["skill_name"]].id if res["skill_name"] in skill_map else None
        resource = LearningResource(
            title=res["title"],
            skill_id=sk_id,
            category="Curated Guide",
            difficulty=res["difficulty"],
            resource_type=res["resource_type"],
            url=res["url"],
            estimated_hours=res["estimated_hours"],
            rating=res["rating"]
        )
        db.add(resource)

    # 4. Seed Questions
    for q in CURATED_QUESTIONS:
        question = Question(
            category=q["category"],
            sub_category=q["sub_category"],
            difficulty=q["difficulty"],
            question_text=q["question_text"],
            options=q["options"],
            correct_answer=q["correct_answer"],
            explanation=q["explanation"]
        )
        db.add(question)

    # 5. Seed Default Demo Student Profile
    user = User(
        id="u0000001-0000-0000-0000-000000000001",
        email="student.demo@smartplacement.edu",
        full_name="Aarav Sharma",
        role="student"
    )
    db.add(user)
    db.flush()

    student_profile = StudentProfile(
        id="p0000001-0000-0000-0000-000000000001",
        user_id=user.id,
        headline="Aspiring Full-Stack & Backend Software Engineer | B.Tech CSE 2026",
        degree="B.Tech",
        branch="Computer Science and Engineering",
        graduation_year=2026,
        cgpa=8.45,
        bio="Passionate about designing scalable distributed APIs, microservices, and reactive web applications. Experienced in Python, FastAPI, React, and PostgreSQL.",
        interests=["Distributed Systems", "Cloud Computing", "Web Architectures", "Machine Learning"],
        target_role_id="b0000001-0000-0000-0000-000000000003" # Backend Developer
    )
    db.add(student_profile)
    db.flush()

    # Initial Skills for Demo Student
    demo_skills = [
        ("Python", "Advanced"),
        ("FastAPI", "Intermediate"),
        ("SQL", "Intermediate"),
        ("JavaScript", "Intermediate"),
        ("React", "Intermediate"),
        ("Git & GitHub", "Intermediate"),
        ("Data Structures & Algorithms", "Intermediate"),
        ("Docker", "Beginner")
    ]
    for sk_name, prof in demo_skills:
        if sk_name in skill_map:
            st_skill = StudentSkill(
                student_profile_id=student_profile.id,
                skill_id=skill_map[sk_name].id,
                proficiency=prof,
                verified=True
            )
            db.add(st_skill)

    # Demo Projects
    demo_project = StudentProject(
        student_profile_id=student_profile.id,
        title="Distributed E-Commerce Microservices",
        description="Built an asynchronous order processing service using FastAPI, Celery, and PostgreSQL with Docker containerization.",
        technologies=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        github_url="https://github.com/demo/ecommerce-microservices",
        live_url="https://demo-ecommerce.example.com"
    )
    db.add(demo_project)

    demo_project_2 = StudentProject(
        student_profile_id=student_profile.id,
        title="Real-Time Collaborative Markdown Editor",
        description="Built a web application with Next.js, React, and WebSockets enabling simultaneous collaborative document editing.",
        technologies=["React", "TypeScript", "Next.js", "Node.js"],
        github_url="https://github.com/demo/collaborative-editor"
    )
    db.add(demo_project_2)

    # Demo Certification
    cert = StudentCertification(
        student_profile_id=student_profile.id,
        title="AWS Certified Cloud Practitioner",
        issuing_organization="Amazon Web Services",
        issue_year=2025,
        credential_url="https://aws.amazon.com/verification/demo"
    )
    db.add(cert)

    # Demo Experience
    exp = StudentExperience(
        student_profile_id=student_profile.id,
        title="Software Engineering Intern",
        company="NexTech Solutions",
        experience_type="Internship",
        start_date="2025-06-01",
        end_date="2025-08-31",
        description="Engineered REST API endpoints in Python, optimized database queries, and implemented automated CI/CD unit testing.",
        skills_used=["Python", "SQL", "Git & GitHub"]
    )
    db.add(exp)

    db.commit()
