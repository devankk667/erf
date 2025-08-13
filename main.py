import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import requests
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class DatabaseManager:
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if self.database_url:
            self.init_database()

    def get_connection(self):
        """Get database connection"""
        if not self.database_url:
            return None
        return psycopg2.connect(self.database_url)

    def init_database(self):
        """Initialize database tables for storing ERD schemas"""
        try:
            conn = self.get_connection()
            if not conn:
                return

            cur = conn.cursor()

            # Create tables for storing ERD schemas
            cur.execute("""
                CREATE TABLE IF NOT EXISTS erd_schemas (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    schema_data JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS erd_visualizations (
                    id SERIAL PRIMARY KEY,
                    schema_id INTEGER REFERENCES erd_schemas(id) ON DELETE CASCADE,
                    image_path VARCHAR(500),
                    sql_path VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            print("✅ Database tables initialized successfully!")

        except psycopg2.Error as e:
            print(f"❌ Database initialization error: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()

    def save_schema(self, name: str, description: str, entities: Dict, relationships: Dict) -> Optional[int]:
        """Save ERD schema to database"""
        if not self.database_url:
            print("⚠️ No database connection available")
            return None

        try:
            conn = self.get_connection()
            cur = conn.cursor()

            schema_data = {
                "entities": entities,
                "relationships": relationships
            }

            cur.execute("""
                INSERT INTO erd_schemas (name, description, schema_data)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, (name, description, json.dumps(schema_data)))

            schema_id = cur.fetchone()[0]
            conn.commit()
            print(f"✅ Schema '{name}' saved to database with ID: {schema_id}")
            return schema_id

        except psycopg2.Error as e:
            print(f"❌ Error saving schema: {e}")
            return None
        finally:
            if conn:
                cur.close()
                conn.close()

    def load_schema(self, schema_id: int) -> Optional[Dict]:
        """Load ERD schema from database"""
        if not self.database_url:
            print("⚠️ No database connection available")
            return None

        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("""
                SELECT * FROM erd_schemas WHERE id = %s;
            """, (schema_id,))

            result = cur.fetchone()
            if result:
                return dict(result)
            else:
                print(f"❌ Schema with ID {schema_id} not found")
                return None

        except psycopg2.Error as e:
            print(f"❌ Error loading schema: {e}")
            return None
        finally:
            if conn:
                cur.close()
                conn.close()

    def list_schemas(self) -> List[Dict]:
        """List all saved ERD schemas"""
        if not self.database_url:
            print("⚠️ No database connection available")
            return []

        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("""
                SELECT id, name, description, created_at, updated_at
                FROM erd_schemas
                ORDER BY updated_at DESC;
            """)

            results = cur.fetchall()
            return [dict(row) for row in results]

        except psycopg2.Error as e:
            print(f"❌ Error listing schemas: {e}")
            return []
        finally:
            if conn:
                cur.close()
                conn.close()

    def delete_schema(self, schema_id: int) -> bool:
        """Delete ERD schema from database"""
        if not self.database_url:
            print("⚠️ No database connection available")
            return False

        try:
            conn = self.get_connection()
            cur = conn.cursor()

            cur.execute("DELETE FROM erd_schemas WHERE id = %s;", (schema_id,))
            
            if cur.rowcount > 0:
                conn.commit()
                print(f"✅ Schema with ID {schema_id} deleted successfully")
                return True
            else:
                print(f"❌ Schema with ID {schema_id} not found")
                return False

        except psycopg2.Error as e:
            print(f"❌ Error deleting schema: {e}")
            return False
        finally:
            if conn:
                cur.close()
                conn.close()

    def save_visualization_info(self, schema_id: int, image_path: str, sql_path: str):
        """Save visualization file paths"""
        if not self.database_url:
            return

        try:
            conn = self.get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO erd_visualizations (schema_id, image_path, sql_path)
                VALUES (%s, %s, %s);
            """, (schema_id, image_path, sql_path))

            conn.commit()

        except psycopg2.Error as e:
            print(f"❌ Error saving visualization info: {e}")
        finally:
            if conn:
                cur.close()
                conn.close()


class ERDGenerator:
    def __init__(self):
        self.G = nx.DiGraph()
        self.entities = {}
        self.relationships = {}
        self.db_manager = DatabaseManager()
        self.current_schema_id = None

    def add_entity(self, name: str, attributes: List[Dict]):
        """Add an entity with its attributes"""
        self.entities[name] = attributes
        self.G.add_node(name, shape="box", node_type="entity")

        for attr in attributes:
            attr_name = f"{name}_{attr['name']}"
            attr_type = attr.get('type', 'VARCHAR')
            is_key = attr.get('is_key', False)
            is_derived = attr.get('is_derived', False)

            # Add attribute node
            self.G.add_node(attr_name, 
                          shape="oval", 
                          node_type="attribute",
                          display_name=f"{attr['name']}\n({attr_type})",
                          is_key=is_key,
                          is_derived=is_derived)

            # Connect entity to attribute
            style = "dotted" if is_derived else "solid"
            self.G.add_edge(name, attr_name, edge_type="attribute", style=style)

    def add_relationship(self, name: str, entities: List[str], attributes: List[Dict] = None):
        """Add a relationship between entities"""
        self.relationships[name] = {'entities': entities, 'attributes': attributes or []}

        # Add relationship node
        self.G.add_node(name, shape="diamond", node_type="relationship")

        # Connect entities to relationship
        for entity in entities:
            self.G.add_edge(entity, name, edge_type="participation")

        # Add relationship attributes
        if attributes:
            for attr in attributes:
                attr_name = f"{name}_{attr['name']}"
                self.G.add_node(attr_name, 
                              shape="oval", 
                              node_type="attribute",
                              display_name=f"{attr['name']}\n({attr.get('type', 'VARCHAR')})")
                self.G.add_edge(name, attr_name, edge_type="attribute")

    def _call_ai_simulation(self, topic: str) -> Dict:
        """
        Simulates a call to an AI service to get an ERD structure.
        In a real implementation, this would make an API call to a service like OpenAI or Claude.
        """
        print("🧠 Simulating AI thinking...")

        # More extensive templates with associated keywords for better matching
        erd_templates = {
            "library": {
                "keywords": ["library", "book", "author", "borrow", "librarian"],
                "schema": {
                    "entities": {
                        "Book": [{"name": "book_id", "type": "INT", "is_key": True}, 
                                {"name": "title", "type": "VARCHAR(255)"}, 
                                {"name": "isbn", "type": "VARCHAR(20)"}],
                        "Author": [{"name": "author_id", "type": "INT", "is_key": True}, 
                                  {"name": "name", "type": "VARCHAR(255)"}],
                        "Member": [{"name": "member_id", "type": "INT", "is_key": True}, 
                                  {"name": "name", "type": "VARCHAR(255)"}, 
                                  {"name": "join_date", "type": "DATE"}]
                    },
                    "relationships": {
                        "Writes": {"entities": ["Author", "Book"]},
                        "Borrows": {"entities": ["Member", "Book"], 
                                   "attributes": [{"name": "borrow_date", "type": "DATE"}]}
                    }
                }
            },
            "ecommerce": {
                "keywords": ["shop", "store", "product", "customer", "order", "purchase"],
                "schema": {
                    "entities": {
                        "Customer": [{"name": "customer_id", "type": "INT", "is_key": True},
                                   {"name": "name", "type": "VARCHAR(255)"},
                                   {"name": "email", "type": "VARCHAR(255)"}],
                        "Product": [{"name": "product_id", "type": "INT", "is_key": True},
                                   {"name": "name", "type": "VARCHAR(255)"},
                                   {"name": "price", "type": "DECIMAL(10,2)"}],
                        "Order": [{"name": "order_id", "type": "INT", "is_key": True},
                                 {"name": "order_date", "type": "DATE"},
                                 {"name": "total", "type": "DECIMAL(10,2)"}]
                    },
                    "relationships": {
                        "Places": {"entities": ["Customer", "Order"]},
                        "Contains": {"entities": ["Order", "Product"],
                                   "attributes": [{"name": "quantity", "type": "INT"}]}
                    }
                }
            },
            "school": {
                "keywords": ["school", "student", "teacher", "course", "class", "grade"],
                "schema": {
                    "entities": {
                        "Student": [{"name": "student_id", "type": "INT", "is_key": True},
                                   {"name": "name", "type": "VARCHAR(255)"},
                                   {"name": "enrollment_date", "type": "DATE"}],
                        "Course": [{"name": "course_id", "type": "INT", "is_key": True},
                                  {"name": "course_name", "type": "VARCHAR(255)"},
                                  {"name": "credits", "type": "INT"}],
                        "Instructor": [{"name": "instructor_id", "type": "INT", "is_key": True},
                                      {"name": "name", "type": "VARCHAR(255)"},
                                      {"name": "department", "type": "VARCHAR(100)"}]
                    },
                    "relationships": {
                        "Enrolls": {"entities": ["Student", "Course"],
                                   "attributes": [{"name": "grade", "type": "CHAR(2)"}]},
                        "Teaches": {"entities": ["Instructor", "Course"]}
                    }
                }
            }
        }

        # Find best matching template
        topic_lower = topic.lower()
        best_match = "library"  # default
        max_score = 0

        for template_name, template_data in erd_templates.items():
            score = sum(1 for keyword in template_data["keywords"] if keyword in topic_lower)
            if score > max_score:
                max_score = score
                best_match = template_name

        print(f"✅ Generated ERD for: {best_match} domain")
        return erd_templates[best_match]["schema"]

    def generate_from_prompt(self, prompt: str, save_to_db: bool = False, schema_name: str = None):
        """Generate ERD from a natural language prompt"""
        schema = self._call_ai_simulation(prompt)

        # Add entities
        for entity_name, attributes in schema["entities"].items():
            self.add_entity(entity_name, attributes)

        # Add relationships
        for rel_name, rel_data in schema["relationships"].items():
            self.add_relationship(rel_name, rel_data["entities"], rel_data.get("attributes", []))

        # Save to database if requested
        if save_to_db and schema_name and self.db_manager.database_url:
            self.current_schema_id = self.db_manager.save_schema(
                schema_name, prompt, self.entities, self.relationships
            )

    def load_from_database(self, schema_id: int):
        """Load ERD from database"""
        schema_data = self.db_manager.load_schema(schema_id)
        if not schema_data:
            return False

        # Clear current data
        self.G.clear()
        self.entities.clear()
        self.relationships.clear()

        # Load entities and relationships
        schema_json = schema_data['schema_data']
        
        for entity_name, attributes in schema_json["entities"].items():
            self.add_entity(entity_name, attributes)

        for rel_name, rel_data in schema_json["relationships"].items():
            self.add_relationship(rel_name, rel_data["entities"], rel_data.get("attributes", []))

        self.current_schema_id = schema_id
        print(f"✅ Loaded schema: {schema_data['name']}")
        return True

    def save_current_schema(self, name: str, description: str = ""):
        """Save current ERD schema to database"""
        if not self.entities:
            print("❌ No schema to save")
            return None

        self.current_schema_id = self.db_manager.save_schema(
            name, description, self.entities, self.relationships
        )
        return self.current_schema_id

    def visualize(self, save_path: str = None, figsize: Tuple[int, int] = (12, 8), ask_save_path: bool = False):
        """Visualize the ERD using matplotlib"""
        if not self.G.nodes():
            print("No entities or relationships to visualize!")
            return

        # Ask user for save path if requested
        if ask_save_path and save_path is None:
            user_path = input("\n📁 Enter the path/filename to save the ERD (or press Enter for default): ").strip()
            if user_path:
                # Ensure .jpg extension
                if not user_path.lower().endswith('.jpg'):
                    user_path += '.jpg'
                save_path = user_path

        plt.figure(figsize=figsize)

        # Create layout
        pos = nx.spring_layout(self.G, k=3, iterations=50)

        # Separate nodes by type
        entities = [n for n, d in self.G.nodes(data=True) if d.get('node_type') == 'entity']
        relationships = [n for n, d in self.G.nodes(data=True) if d.get('node_type') == 'relationship']
        attributes = [n for n, d in self.G.nodes(data=True) if d.get('node_type') == 'attribute']
        key_attrs = [n for n, d in self.G.nodes(data=True) if d.get('is_key', False)]

        # Draw entities (rectangles)
        nx.draw_networkx_nodes(self.G, pos, nodelist=entities, 
                              node_color='lightblue', node_shape='s', 
                              node_size=3000, alpha=0.8)

        # Draw relationships (diamonds)
        nx.draw_networkx_nodes(self.G, pos, nodelist=relationships, 
                              node_color='lightgreen', node_shape='D', 
                              node_size=2000, alpha=0.8)

        # Draw regular attributes (circles)
        regular_attrs = [n for n in attributes if n not in key_attrs]
        nx.draw_networkx_nodes(self.G, pos, nodelist=regular_attrs, 
                              node_color='lightyellow', node_shape='o', 
                              node_size=1000, alpha=0.8)

        # Draw key attributes (circles with border)
        nx.draw_networkx_nodes(self.G, pos, nodelist=key_attrs, 
                              node_color='gold', node_shape='o', 
                              node_size=1000, alpha=0.8, edgecolors='red', linewidths=2)

        # Draw edges
        participation_edges = [(u, v) for u, v, d in self.G.edges(data=True) 
                              if d.get('edge_type') == 'participation']
        attribute_edges = [(u, v) for u, v, d in self.G.edges(data=True) 
                          if d.get('edge_type') == 'attribute']

        nx.draw_networkx_edges(self.G, pos, edgelist=participation_edges, 
                              edge_color='black', width=2)
        nx.draw_networkx_edges(self.G, pos, edgelist=attribute_edges, 
                              edge_color='gray', width=1)

        # Add labels
        labels = {}
        for node, data in self.G.nodes(data=True):
            if data.get('node_type') == 'attribute':
                labels[node] = data.get('display_name', node.split('_')[-1])
            else:
                labels[node] = node

        nx.draw_networkx_labels(self.G, pos, labels, font_size=8, font_weight='bold')

        # Create legend
        legend_elements = [
            mpatches.Rectangle((0, 0), 1, 1, facecolor='lightblue', label='Entity'),
            mpatches.Polygon([(0, 0), (0.5, 0.5), (1, 0), (0.5, -0.5)], 
                           facecolor='lightgreen', label='Relationship'),
            plt.Circle((0, 0), 0.5, facecolor='lightyellow', label='Attribute'),
            plt.Circle((0, 0), 0.5, facecolor='gold', edgecolor='red', 
                      linewidth=2, label='Key Attribute')
        ]

        plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
        plt.title("Entity-Relationship Diagram", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()

        if save_path:
            try:
                plt.savefig(save_path, format='jpeg', dpi=300, bbox_inches='tight')
                print(f"ERD saved to {save_path}")

                # Save visualization info to database if we have a current schema
                if self.current_schema_id and self.db_manager.database_url:
                    sql_path = save_path.replace('.jpg', '_schema.sql')
                    self.db_manager.save_visualization_info(self.current_schema_id, save_path, sql_path)
            except Exception as e:
                print(f"Error saving ERD: {e}")

        # Don't call plt.show() in headless environment
        try:
            plt.show()
        except Exception:
            print("Note: Running in headless mode - ERD saved to file")

    def export_to_sql(self) -> str:
        """Export the ERD to SQL CREATE TABLE statements"""
        sql_statements = []

        # Create tables for entities
        for entity_name, attributes in self.entities.items():
            sql = f"CREATE TABLE {entity_name} (\n"
            attr_definitions = []
            primary_keys = []

            for attr in attributes:
                attr_def = f"    {attr['name']} {attr['type']}"
                if attr.get('is_key'):
                    primary_keys.append(attr['name'])
                attr_definitions.append(attr_def)

            sql += ",\n".join(attr_definitions)

            if primary_keys:
                sql += f",\n    PRIMARY KEY ({', '.join(primary_keys)})"

            sql += "\n);"
            sql_statements.append(sql)

        # Add foreign key constraints for relationships
        for rel_name, rel_data in self.relationships.items():
            if len(rel_data['entities']) == 2:
                # Binary relationship - add foreign key
                entity1, entity2 = rel_data['entities']
                
                # Find primary keys
                entity1_pk = next((attr['name'] for attr in self.entities[entity1] if attr.get('is_key')), f"{entity1.lower()}_id")
                entity2_pk = next((attr['name'] for attr in self.entities[entity2] if attr.get('is_key')), f"{entity2.lower()}_id")
                
                # Create relationship table if it has attributes
                if rel_data.get('attributes'):
                    rel_table_sql = f"CREATE TABLE {rel_name} (\n"
                    rel_attr_defs = [
                        f"    {entity1_pk} {self._get_pk_type(entity1)}",
                        f"    {entity2_pk} {self._get_pk_type(entity2)}"
                    ]
                    
                    for attr in rel_data['attributes']:
                        rel_attr_defs.append(f"    {attr['name']} {attr['type']}")
                    
                    rel_table_sql += ",\n".join(rel_attr_defs)
                    rel_table_sql += f",\n    PRIMARY KEY ({entity1_pk}, {entity2_pk})"
                    rel_table_sql += f",\n    FOREIGN KEY ({entity1_pk}) REFERENCES {entity1}({entity1_pk})"
                    rel_table_sql += f",\n    FOREIGN KEY ({entity2_pk}) REFERENCES {entity2}({entity2_pk})"
                    rel_table_sql += "\n);"
                    sql_statements.append(rel_table_sql)

        return "\n\n".join(sql_statements)

    def _get_pk_type(self, entity_name: str) -> str:
        """Get the primary key type for an entity"""
        for attr in self.entities[entity_name]:
            if attr.get('is_key'):
                return attr['type']
        return "INT"

    def save_sql_to_file(self, filename: str = "schema.sql"):
        """Save SQL statements to a file"""
        sql_content = self.export_to_sql()
        with open(filename, 'w') as f:
            f.write(sql_content)
        print(f"SQL schema saved to {filename}")

    def generate_sample_data(self) -> str:
        """Generate sample INSERT statements for testing"""
        insert_statements = []
        
        sample_data = {
            "Book": [
                {"book_id": 1, "title": "'The Great Gatsby'", "isbn": "'978-0-7432-7356-5'"},
                {"book_id": 2, "title": "'To Kill a Mockingbird'", "isbn": "'978-0-06-112008-4'"},
                {"book_id": 3, "title": "'1984'", "isbn": "'978-0-452-28423-4'"}
            ],
            "Author": [
                {"author_id": 1, "name": "'F. Scott Fitzgerald'"},
                {"author_id": 2, "name": "'Harper Lee'"},
                {"author_id": 3, "name": "'George Orwell'"}
            ],
            "Member": [
                {"member_id": 1, "name": "'John Doe'", "join_date": "'2023-01-15'"},
                {"member_id": 2, "name": "'Jane Smith'", "join_date": "'2023-02-20'"},
                {"member_id": 3, "name": "'Bob Johnson'", "join_date": "'2023-03-10'"}
            ],
            "Customer": [
                {"customer_id": 1, "name": "'Alice Johnson'", "email": "'alice@email.com'"},
                {"customer_id": 2, "name": "'Bob Smith'", "email": "'bob@email.com'"},
                {"customer_id": 3, "name": "'Carol Davis'", "email": "'carol@email.com'"}
            ],
            "Product": [
                {"product_id": 1, "name": "'Laptop'", "price": "999.99"},
                {"product_id": 2, "name": "'Mouse'", "price": "29.99"},
                {"product_id": 3, "name": "'Keyboard'", "price": "79.99"}
            ],
            "Order": [
                {"order_id": 1, "order_date": "'2023-06-01'", "total": "999.99"},
                {"order_id": 2, "order_date": "'2023-06-02'", "total": "109.98"},
                {"order_id": 3, "order_date": "'2023-06-03'", "total": "79.99"}
            ],
            "Student": [
                {"student_id": 1, "name": "'Emily Chen'", "enrollment_date": "'2023-09-01'"},
                {"student_id": 2, "name": "'Michael Brown'", "enrollment_date": "'2023-09-01'"},
                {"student_id": 3, "name": "'Sarah Wilson'", "enrollment_date": "'2023-09-02'"}
            ],
            "Course": [
                {"course_id": 1, "course_name": "'Introduction to Computer Science'", "credits": "3"},
                {"course_id": 2, "course_name": "'Calculus I'", "credits": "4"},
                {"course_id": 3, "course_name": "'English Literature'", "credits": "3"}
            ],
            "Instructor": [
                {"instructor_id": 1, "name": "'Dr. Robert Taylor'", "department": "'Computer Science'"},
                {"instructor_id": 2, "name": "'Dr. Lisa Anderson'", "department": "'Mathematics'"},
                {"instructor_id": 3, "name": "'Prof. James White'", "department": "'English'"}
            ]
        }
        
        # Generate INSERT statements for existing entities
        for entity_name in self.entities.keys():
            if entity_name in sample_data:
                for record in sample_data[entity_name]:
                    columns = ", ".join(record.keys())
                    values = ", ".join(str(v) for v in record.values())
                    insert_statements.append(f"INSERT INTO {entity_name} ({columns}) VALUES ({values});")
        
        return "\n".join(insert_statements)

    def print_summary(self):
        """Print a summary of the ERD"""
        print("\n" + "="*50)
        print("ERD SUMMARY")
        print("="*50)

        print(f"\nEntities ({len(self.entities)}):")
        for entity, attributes in self.entities.items():
            print(f"  • {entity}")
            for attr in attributes:
                key_indicator = " (KEY)" if attr.get('is_key') else ""
                print(f"    - {attr['name']}: {attr.get('type', 'VARCHAR')}{key_indicator}")

        print(f"\nRelationships ({len(self.relationships)}):")
        for rel_name, rel_data in self.relationships.items():
            entities_str = " ↔ ".join(rel_data['entities'])
            print(f"  • {rel_name}: {entities_str}")
            if rel_data.get('attributes'):
                for attr in rel_data['attributes']:
                    print(f"    - {attr['name']}: {attr.get('type', 'VARCHAR')}")


def database_menu(erd: ERDGenerator):
    """Database management menu"""
    while True:
        print("\n" + "="*50)
        print("DATABASE MANAGEMENT")
        print("="*50)
        print("1. Save current schema to database")
        print("2. Load schema from database")
        print("3. List all saved schemas")
        print("4. Delete schema from database")
        print("5. Back to main menu")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            if not erd.entities:
                print("❌ No schema loaded to save")
                continue
            name = input("Enter schema name: ").strip()
            if name:
                description = input("Enter description (optional): ").strip()
                erd.save_current_schema(name, description)
        
        elif choice == '2':
            schemas = erd.db_manager.list_schemas()
            if not schemas:
                print("❌ No schemas found in database")
                continue
                
            print("\nAvailable schemas:")
            for schema in schemas:
                print(f"{schema['id']}: {schema['name']} - {schema['description'][:50]}...")
                print(f"   Created: {schema['created_at']}")
            
            try:
                schema_id = int(input("\nEnter schema ID to load: "))
                if erd.load_from_database(schema_id):
                    print("Schema loaded successfully!")
                    return  # Return to main menu after loading
            except ValueError:
                print("❌ Invalid ID entered")
        
        elif choice == '3':
            schemas = erd.db_manager.list_schemas()
            if not schemas:
                print("❌ No schemas found in database")
                continue
                
            print("\nSaved schemas:")
            print("-" * 80)
            for schema in schemas:
                print(f"ID: {schema['id']}")
                print(f"Name: {schema['name']}")
                print(f"Description: {schema['description']}")
                print(f"Created: {schema['created_at']}")
                print(f"Updated: {schema['updated_at']}")
                print("-" * 80)
        
        elif choice == '4':
            schemas = erd.db_manager.list_schemas()
            if not schemas:
                print("❌ No schemas found in database")
                continue
                
            print("\nAvailable schemas:")
            for schema in schemas:
                print(f"{schema['id']}: {schema['name']}")
            
            try:
                schema_id = int(input("\nEnter schema ID to delete: "))
                confirm = input(f"Are you sure you want to delete schema {schema_id}? (y/N): ").strip().lower()
                if confirm == 'y':
                    erd.db_manager.delete_schema(schema_id)
            except ValueError:
                print("❌ Invalid ID entered")
        
        elif choice == '5':
            break
        
        else:
            print("❌ Invalid choice")


def main():
    print("🎯 ERD Generator - Create Entity-Relationship Diagrams from Natural Language")
    print("=" * 70)

    # Check database connection
    if 'DATABASE_URL' in os.environ:
        print("✅ Database connection available")
    else:
        print("⚠️ No database connection - database features disabled")
        print("   Set up PostgreSQL database in Replit to enable database features")

    # Create ERD generator
    erd = ERDGenerator()

    # Example 1: Library System
    print("\n📚 Example 1: Generating Library Management System ERD")
    erd.generate_from_prompt("Create a library management system with books, authors, and members")
    erd.print_summary()
    erd.visualize(save_path="library_erd.jpg")
    
    # Save SQL schema and sample data
    erd.save_sql_to_file("library_schema.sql")
    print("\n📝 Sample Data for Library System:")
    sample_data = erd.generate_sample_data()
    with open("library_sample_data.sql", 'w') as f:
        f.write(sample_data)
    print("Sample data saved to library_sample_data.sql")

    # Clear for next example
    erd = ERDGenerator()

    # Example 2: E-commerce System
    print("\n🛒 Example 2: Generating E-commerce System ERD")
    erd.generate_from_prompt("Design an online shopping platform with customers, products, and orders")
    erd.print_summary()
    erd.visualize(save_path="ecommerce_erd.jpg")

    # Export to SQL
    print("\n💾 SQL Schema Export:")
    print(erd.export_to_sql())
    erd.save_sql_to_file("ecommerce_schema.sql")
    
    print("\n📝 Sample Data for E-commerce System:")
    sample_data = erd.generate_sample_data()
    with open("ecommerce_sample_data.sql", 'w') as f:
        f.write(sample_data)
    print("Sample data saved to ecommerce_sample_data.sql")

    # Interactive mode
    print("\n🎮 Interactive Mode:")
    print("Choose an option:")
    print("1. Create new ERD from description")
    print("2. Database management")
    print("3. Exit")

    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            user_input = input("\n> Describe your system: ").strip()

            if user_input:
                erd = ERDGenerator()
                
                # Ask if user wants to save to database
                save_to_db = False
                schema_name = None
                if erd.db_manager.database_url:
                    save_choice = input("Save to database? (y/N): ").strip().lower()
                    if save_choice == 'y':
                        save_to_db = True
                        schema_name = input("Enter schema name: ").strip() or user_input[:30]
                
                erd.generate_from_prompt(user_input, save_to_db=save_to_db, schema_name=schema_name)
                erd.print_summary()
                
                # Generate filename based on input
                filename_base = user_input.lower().replace(' ', '_')[:20]
                erd.visualize(save_path=f"{filename_base}_erd.jpg")
                erd.save_sql_to_file(f"{filename_base}_schema.sql")
                
                # Generate and save sample data
                sample_data = erd.generate_sample_data()
                if sample_data:
                    with open(f"{filename_base}_sample_data.sql", 'w') as f:
                        f.write(sample_data)
                    print(f"Sample data saved to {filename_base}_sample_data.sql")
        
        elif choice == '2':
            if not erd.db_manager.database_url:
                print("❌ Database not available. Set up PostgreSQL database in Replit.")
                continue
            database_menu(erd)
        
        elif choice == '3':
            break
        
        else:
            print("❌ Invalid choice")

    print("\n👋 Thanks for using ERD Generator!")


if __name__ == "__main__":
    main()