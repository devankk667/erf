import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import requests
from typing import Dict, List, Tuple

class ERDGenerator:
    def __init__(self):
        self.G = nx.DiGraph()
        self.entities = {}
        self.relationships = {}

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

    def generate_from_prompt(self, prompt: str):
        """Generate ERD from a natural language prompt"""
        schema = self._call_ai_simulation(prompt)

        # Add entities
        for entity_name, attributes in schema["entities"].items():
            self.add_entity(entity_name, attributes)

        # Add relationships
        for rel_name, rel_data in schema["relationships"].items():
            self.add_relationship(rel_name, rel_data["entities"], rel_data.get("attributes", []))

    def visualize(self, save_path: str = None, figsize: Tuple[int, int] = (12, 8)):
        """Visualize the ERD using matplotlib"""
        if not self.G.nodes():
            print("No entities or relationships to visualize!")
            return

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
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"ERD saved to {save_path}")

        plt.show()

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

        return "\n\n".join(sql_statements)

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


def main():
    print("🎯 ERD Generator - Create Entity-Relationship Diagrams from Natural Language")
    print("=" * 70)

    # Create ERD generator
    erd = ERDGenerator()

    # Example 1: Library System
    print("\n📚 Example 1: Generating Library Management System ERD")
    erd.generate_from_prompt("Create a library management system with books, authors, and members")
    erd.print_summary()
    erd.visualize(save_path="library_erd.png")

    # Clear for next example
    erd = ERDGenerator()

    # Example 2: E-commerce System
    print("\n🛒 Example 2: Generating E-commerce System ERD")
    erd.generate_from_prompt("Design an online shopping platform with customers, products, and orders")
    erd.print_summary()
    erd.visualize(save_path="ecommerce_erd.png")

    # Export to SQL
    print("\n💾 SQL Export:")
    print(erd.export_to_sql())

    # Interactive mode
    print("\n🎮 Interactive Mode:")
    print("Enter your own description (or 'quit' to exit):")

    while True:
        user_input = input("\n> Describe your system: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            break

        if user_input:
            erd = ERDGenerator()
            erd.generate_from_prompt(user_input)
            erd.print_summary()
            erd.visualize()

    print("\n👋 Thanks for using ERD Generator!")


if __name__ == "__main__":
    main()