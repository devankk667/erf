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
                        "Book": [{"name": "book_id", "type": "INT", "is_key": True}, {"name": "title", "type": "VARCHAR(255)"}, {"name": "isbn", "type": "VARCHAR(20)"}],
                        "Author": [{"name": "author_id", "type": "INT", "is_key": True}, {"name": "name", "type": "VARCHAR(255)"}],
                        "Member": [{"name": "member_id", "type": "INT", "is_key": True}, {"name": "name", "type": "VARCHAR(255)"}, {"name": "join_date", "type": "DATE"}]
                    },
                    "relationships": {
                        "Writes": {"entities": ["Author", "Book"], "attributes": []},
                        "Borrows": {"entities": ["Member", "Book"], "attributes": [{"name": "borrow_date", "type": "DATE"}]}
                    }
                }
            },
            "ecommerce": {
                "keywords": ["ecommerce", "shop", "store", "product", "customer", "order", "cart"],
                "schema": {
                    "entities": {
                        "Customer": [{"name": "customer_id", "type": "INT", "is_key": True}, {"name": "name", "type": "VARCHAR(255)"}, {"name": "email", "type": "VARCHAR(255)"}],
                        "Product": [{"name": "product_id", "type": "INT", "is_key": True}, {"name": "name", "type": "VARCHAR(255)"}, {"name": "price", "type": "DECIMAL(10,2)"}],
                        "Order": [{"name": "order_id", "type": "INT", "is_key": True}, {"name": "order_date", "type": "DATE"}]
                    },
                    "relationships": {
                        "Places": {"entities": ["Customer", "Order"], "attributes": []},
                        "Contains": {"entities": ["Order", "Product"], "attributes": [{"name": "quantity", "type": "INT"}]}
                    }
                }
            },
            "school": {
                "keywords": ["school", "student", "teacher", "course", "college", "university"],
                "schema": {
                    "entities": {
                        "Student": [{"name": "student_id", "type": "INT", "is_key": True}, {"name": "name", "type": "VARCHAR(255)"}, {"name": "enrollment_date", "type": "DATE"}],
                        "Teacher": [{"name": "teacher_id", "type": "INT", "is_key": True}, {"name": "name", "type": "VARCHAR(255)"}, {"name": "department", "type": "VARCHAR(100)"}],
                        "Course": [{"name": "course_id", "type": "INT", "is_key": True}, {"name": "title", "type": "VARCHAR(255)"}, {"name": "credits", "type": "INT"}]
                    },
                    "relationships": {
                        "Enrolls": {"entities": ["Student", "Course"], "attributes": [{"name": "grade", "type": "CHAR(1)"}]},
                        "Teaches": {"entities": ["Teacher", "Course"], "attributes": []}
                    }
                }
            }
        }
        
        # Find the best matching template based on keyword scores
        topic_lower = topic.lower()
        scores = {}
        for name, template in erd_templates.items():
            score = sum(1 for keyword in template["keywords"] if keyword in topic_lower)
            scores[name] = score

        best_match = max(scores, key=scores.get) if any(s > 0 for s in scores.values()) else None

        if best_match:
            print(f"🤖 AI selected the '{best_match}' template.")
            return erd_templates[best_match]["schema"]
        else:
            # Default fallback if no keywords match
            print("🤖 AI couldn't find a matching template, creating a default one.")
            return {
                "entities": {
                    topic.title(): [
                        {"name": "id", "type": "INT", "is_key": True},
                        {"name": "name", "type": "VARCHAR(255)"},
                        {"name": "description", "type": "TEXT"}
                    ]
                },
                "relationships": {}
            }

    def generate_from_ai(self, topic: str):
        """Generate ERD from topic using a simulated AI call"""
        print(f"🤖 Generating ERD for topic: '{topic}'...")
        
        # Get the ERD structure from the simulated AI
        template = self._call_ai_simulation(topic)

        # Clear existing graph and build from the template
        self.G.clear()
        self.entities.clear()
        self.relationships.clear()
        
        # Add entities from the template
        for entity_name, attributes in template["entities"].items():
            self.add_entity(entity_name, attributes)
        
        # Add relationships from the template
        for rel_name, rel_data in template["relationships"].items():
            self.add_relationship(rel_name, rel_data["entities"], rel_data.get("attributes"))
        
        print(f"✅ Generated ERD with {len(self.entities)} entities and {len(self.relationships)} relationships")
    
    def interactive_input(self):
        """Interactive mode for manual ERD creation with improved UX"""
        print("\n🎯 Interactive ERD Builder")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("1. Add Entity")
            print("2. Add Relationship")
            print("3. View Current ERD")
            print("4. Generate Visualization")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self._add_entity_interactive()
            elif choice == "2":
                self._add_relationship_interactive()
            elif choice == "3":
                self.view_summary()
            elif choice == "4":
                self.visualize()
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice. Please try again.")

    def _add_entity_interactive(self):
        """Interactive entity creation with validation"""
        entity_name = input("\nEnter entity name: ").strip()
        if not entity_name:
            print("❌ Entity name cannot be empty.")
            return
        if entity_name in self.entities:
            print(f"❌ Entity '{entity_name}' already exists.")
            return
        
        attributes = []
        existing_attr_names = set()
        print(f"\nAdding attributes for '{entity_name}' (press Enter with empty name to finish):")
        
        while True:
            attr_name = input("  Attribute name: ").strip()
            if not attr_name:
                break
            if attr_name in existing_attr_names:
                print(f"❌ Attribute '{attr_name}' already added to this entity.")
                continue
                
            attr_type = input(f"  Type for '{attr_name}' (default: VARCHAR): ").strip() or "VARCHAR"
            is_key = input(f"  Is '{attr_name}' a primary key? (y/n): ").strip().lower() == 'y'
            is_derived = input(f"  Is '{attr_name}' derived? (y/n): ").strip().lower() == 'y'
            
            attributes.append({"name": attr_name, "type": attr_type, "is_key": is_key, "is_derived": is_derived})
            existing_attr_names.add(attr_name)
        
        if not attributes:
            print("⚠️ No attributes added. Entity not created.")
            return

        self.add_entity(entity_name, attributes)
        print(f"✅ Added entity '{entity_name}' with {len(attributes)} attributes.")

    def _add_relationship_interactive(self):
        """Interactive relationship creation with validation"""
        if len(self.entities) < 1:
            print("❌ You must add at least one entity before creating a relationship.")
            return
        
        print("\nAvailable entities:")
        for e in self.entities:
            print(f"- {e}")

        rel_name = input("Enter relationship name (e.g., 'WorksIn'): ").strip()
        if not rel_name:
            print("❌ Relationship name cannot be empty.")
            return
        if rel_name in self.relationships:
            print(f"❌ Relationship '{rel_name}' already exists.")
            return

        entities_in_rel = []
        print("Enter entities for this relationship (one per line, press Enter to finish):")
        while True:
            entity_name = input("  Entity name: ").strip()
            if not entity_name:
                break
            if entity_name not in self.entities:
                print(f"❌ Entity '{entity_name}' not found. Please choose from the list above.")
            elif entity_name in entities_in_rel:
                print(f"❌ Entity '{entity_name}' already added to this relationship.")
            else:
                entities_in_rel.append(entity_name)
        
        if len(entities_in_rel) < 2:
            print("❌ A relationship requires at least two distinct entities.")
            return

        attributes = []
        if input("Add attributes to this relationship? (y/n): ").strip().lower() == 'y':
            print(f"\nAdding attributes for '{rel_name}' (press Enter with empty name to finish):")
            while True:
                attr_name = input("  Attribute name: ").strip()
                if not attr_name:
                    break
                attr_type = input(f"  Type for '{attr_name}' (default: VARCHAR): ").strip() or "VARCHAR"
                attributes.append({"name": attr_name, "type": attr_type})

        self.add_relationship(rel_name, entities_in_rel, attributes)
        print(f"✅ Added relationship '{rel_name}' between {entities_in_rel}.")

    def view_summary(self):
        """Prints a summary of the current ERD"""
        print("\n📋 Current ERD Summary")
        print("=" * 40)
        if not self.entities:
            print("ERD is currently empty.")
            return

        print("Entities:")
        for name, attrs in self.entities.items():
            attr_strs = [f"{a['name']} ({a['type']}){' [PK]' if a.get('is_key') else ''}" for a in attrs]
            print(f"- {name}: {', '.join(attr_strs)}")

        if self.relationships:
            print("\nRelationships:")
            for name, rel in self.relationships.items():
                entities = ' -- '.join(rel['entities'])
                attr_str = ""
                if rel.get('attributes'):
                    attr_strs = [f"{a['name']} ({a['type']})" for a in rel['attributes']]
                    attr_str = f" (Attributes: {', '.join(attr_strs)})"
                print(f"- {name}: {entities}{attr_str}")
    
    def visualize(self):
        """Visualize the ERD"""
        if not self.G.nodes():
            print("❌ No entities to visualize. Add some entities first!")
            return
        
        # Create the layout
        pos = nx.spring_layout(self.G, k=3, iterations=50, seed=42)
        
        # Set up the plot
        plt.figure(figsize=(14, 10))
        plt.title("Entity-Relationship Diagram", fontsize=16, fontweight='bold')
        
        # Define colors for different node types
        colors = {
            'entity': 'lightblue',
            'attribute': 'lightgreen', 
            'relationship': 'lightyellow'
        }
        
        # Draw nodes by type with different shapes and colors
        for node in self.G.nodes():
            node_data = self.G.nodes[node]
            shape = node_data.get('shape', 'box')
            node_type = node_data.get('node_type', 'entity')
            is_key = node_data.get('is_key', False)
            color = colors.get(node_type, 'lightgray')
            
            # Use gold color for primary keys
            if is_key:
                color = 'gold'
            
            if shape == "box":  # Entities
                nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_shape="s", 
                                     node_size=4000, node_color=color, 
                                     edgecolors='black', linewidths=3)
            elif shape == "oval":  # Attributes
                nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_shape="o", 
                                     node_size=2500, node_color=color,
                                     edgecolors='black', linewidths=2)
            elif shape == "diamond":  # Relationships
                nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_shape="D", 
                                     node_size=3500, node_color=color,
                                     edgecolors='black', linewidths=2)
        
        # Draw edges with different styles
        solid_edges = [(u, v) for u, v, d in self.G.edges(data=True) if d.get('style', 'solid') == 'solid']
        dotted_edges = [(u, v) for u, v, d in self.G.edges(data=True) if d.get('style') == 'dotted']
        
        # Draw solid edges
        if solid_edges:
            nx.draw_networkx_edges(self.G, pos, edgelist=solid_edges, edge_color="black", 
                                  arrowsize=20, arrowstyle='->', width=1.5)
        
        # Draw dotted edges (for derived attributes)
        if dotted_edges:
            nx.draw_networkx_edges(self.G, pos, edgelist=dotted_edges, edge_color="red", 
                                  arrowsize=20, arrowstyle='->', width=1.5, style='dashed')
        
        # Draw labels with custom display names
        labels = {}
        for node in self.G.nodes():
            node_data = self.G.nodes[node]
            if 'display_name' in node_data:
                labels[node] = node_data['display_name']
            else:
                labels[node] = node
        
        nx.draw_networkx_labels(self.G, pos, labels, font_size=8, font_weight='bold')
        
        # Create legend
        entity_patch = mpatches.Patch(color='lightblue', label='Entity')
        attribute_patch = mpatches.Patch(color='lightgreen', label='Attribute')
        relationship_patch = mpatches.Patch(color='lightyellow', label='Relationship')
        key_patch = mpatches.Patch(color='gold', label='Primary Key')
        derived_line = mpatches.Patch(color='red', label='Derived Attribute')
        
        plt.legend(handles=[entity_patch, attribute_patch, relationship_patch, key_patch, derived_line], 
                  loc='upper right')
        
        # Remove axes and show
        plt.axis('off')
        plt.tight_layout()
        plt.show()
        
        print("✅ ERD Visualization Complete!")

def main():
    """Main function to run the ERD generator with a persistent loop"""
    erd = ERDGenerator()
    
    while True:
        print("\n🎨 Advanced ERD Generator")
        print("=" * 50)
        print("Choose mode:")
        print("1. Interactive Mode (Manual Input)")
        print("2. AI Generation from Topic")
        print("3. Demo Mode (Library System)")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            erd.interactive_input()
        elif choice == "2":
            topic = input("Enter topic for AI generation: ").strip()
            if topic:
                erd.generate_from_ai(topic)
                erd.visualize()
            else:
                print("❌ Topic cannot be empty.")
        elif choice == "3":
            print("🎭 Running demo with Library Management System...")
            erd.generate_from_ai("library")
            erd.visualize()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()