
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
import os
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
            if entity in self.entities:  # Safety check
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
        """Enhanced AI simulation with more comprehensive templates"""
        print("🧠 Analyzing topic with AI simulation...")
        
        # Expanded template collection
        erd_templates = {
            "library": {
                "keywords": ["library", "book", "author", "borrow", "librarian", "reading"],
                "schema": {
                    "entities": {
                        "Book": [
                            {"name": "book_id", "type": "INT", "is_key": True}, 
                            {"name": "title", "type": "VARCHAR(255)"}, 
                            {"name": "isbn", "type": "VARCHAR(20)"},
                            {"name": "publication_year", "type": "INT"},
                            {"name": "genre", "type": "VARCHAR(100)"}
                        ],
                        "Author": [
                            {"name": "author_id", "type": "INT", "is_key": True}, 
                            {"name": "name", "type": "VARCHAR(255)"},
                            {"name": "birth_date", "type": "DATE"},
                            {"name": "nationality", "type": "VARCHAR(100)"}
                        ],
                        "Member": [
                            {"name": "member_id", "type": "INT", "is_key": True}, 
                            {"name": "name", "type": "VARCHAR(255)"}, 
                            {"name": "join_date", "type": "DATE"},
                            {"name": "phone", "type": "VARCHAR(15)"}
                        ]
                    },
                    "relationships": {
                        "Writes": {"entities": ["Author", "Book"], "attributes": []},
                        "Borrows": {"entities": ["Member", "Book"], "attributes": [
                            {"name": "borrow_date", "type": "DATE"},
                            {"name": "return_date", "type": "DATE"}
                        ]}
                    }
                }
            },
            "ecommerce": {
                "keywords": ["ecommerce", "shop", "store", "product", "customer", "order", "cart", "retail"],
                "schema": {
                    "entities": {
                        "Customer": [
                            {"name": "customer_id", "type": "INT", "is_key": True}, 
                            {"name": "name", "type": "VARCHAR(255)"}, 
                            {"name": "email", "type": "VARCHAR(255)"},
                            {"name": "address", "type": "TEXT"}
                        ],
                        "Product": [
                            {"name": "product_id", "type": "INT", "is_key": True}, 
                            {"name": "name", "type": "VARCHAR(255)"}, 
                            {"name": "price", "type": "DECIMAL(10,2)"},
                            {"name": "stock_quantity", "type": "INT"}
                        ],
                        "Order": [
                            {"name": "order_id", "type": "INT", "is_key": True}, 
                            {"name": "order_date", "type": "DATE"},
                            {"name": "total_amount", "type": "DECIMAL(10,2)"}
                        ]
                    },
                    "relationships": {
                        "Places": {"entities": ["Customer", "Order"], "attributes": []},
                        "Contains": {"entities": ["Order", "Product"], "attributes": [
                            {"name": "quantity", "type": "INT"},
                            {"name": "unit_price", "type": "DECIMAL(10,2)"}
                        ]}
                    }
                }
            },
            "school": {
                "keywords": ["school", "student", "teacher", "course", "college", "university", "education"],
                "schema": {
                    "entities": {
                        "Student": [
                            {"name": "student_id", "type": "INT", "is_key": True}, 
                            {"name": "name", "type": "VARCHAR(255)"}, 
                            {"name": "enrollment_date", "type": "DATE"},
                            {"name": "major", "type": "VARCHAR(100)"}
                        ],
                        "Teacher": [
                            {"name": "teacher_id", "type": "INT", "is_key": True}, 
                            {"name": "name", "type": "VARCHAR(255)"}, 
                            {"name": "department", "type": "VARCHAR(100)"},
                            {"name": "hire_date", "type": "DATE"}
                        ],
                        "Course": [
                            {"name": "course_id", "type": "INT", "is_key": True}, 
                            {"name": "title", "type": "VARCHAR(255)"}, 
                            {"name": "credits", "type": "INT"},
                            {"name": "semester", "type": "VARCHAR(20)"}
                        ]
                    },
                    "relationships": {
                        "Enrolls": {"entities": ["Student", "Course"], "attributes": [
                            {"name": "grade", "type": "CHAR(2)"},
                            {"name": "enrollment_date", "type": "DATE"}
                        ]},
                        "Teaches": {"entities": ["Teacher", "Course"], "attributes": []}
                    }
                }
            },
            "hospital": {
                "keywords": ["hospital", "patient", "doctor", "medical", "healthcare", "clinic"],
                "schema": {
                    "entities": {
                        "Patient": [
                            {"name": "patient_id", "type": "INT", "is_key": True},
                            {"name": "name", "type": "VARCHAR(255)"},
                            {"name": "birth_date", "type": "DATE"},
                            {"name": "phone", "type": "VARCHAR(15)"}
                        ],
                        "Doctor": [
                            {"name": "doctor_id", "type": "INT", "is_key": True},
                            {"name": "name", "type": "VARCHAR(255)"},
                            {"name": "specialization", "type": "VARCHAR(100)"}
                        ],
                        "Appointment": [
                            {"name": "appointment_id", "type": "INT", "is_key": True},
                            {"name": "appointment_date", "type": "DATETIME"},
                            {"name": "duration", "type": "INT"}
                        ]
                    },
                    "relationships": {
                        "Schedules": {"entities": ["Patient", "Appointment"], "attributes": []},
                        "Attends": {"entities": ["Doctor", "Appointment"], "attributes": []}
                    }
                }
            }
        }
        
        # Find best matching template
        topic_lower = topic.lower()
        scores = {}
        for name, template in erd_templates.items():
            score = sum(1 for keyword in template["keywords"] if keyword in topic_lower)
            scores[name] = score

        best_match = max(scores, key=scores.get) if any(s > 0 for s in scores.values()) else None

        if best_match:
            print(f"🤖 AI selected the '{best_match}' domain template.")
            return erd_templates[best_match]["schema"]
        else:
            print("🤖 Creating generic template for custom topic.")
            return {
                "entities": {
                    topic.title(): [
                        {"name": "id", "type": "INT", "is_key": True},
                        {"name": "name", "type": "VARCHAR(255)"},
                        {"name": "description", "type": "TEXT"},
                        {"name": "created_date", "type": "DATETIME"}
                    ]
                },
                "relationships": {}
            }

    def generate_from_ai(self, topic: str):
        """Generate ERD from topic using enhanced AI simulation"""
        print(f"🤖 Generating ERD for topic: '{topic}'...")
        
        template = self._call_ai_simulation(topic)

        # Clear and rebuild
        self.G.clear()
        self.entities.clear()
        self.relationships.clear()
        
        # Add entities
        for entity_name, attributes in template["entities"].items():
            self.add_entity(entity_name, attributes)
        
        # Add relationships
        for rel_name, rel_data in template["relationships"].items():
            self.add_relationship(rel_name, rel_data["entities"], rel_data.get("attributes"))
        
        print(f"✅ Generated ERD with {len(self.entities)} entities and {len(self.relationships)} relationships")
    
    def export_to_json(self, filename: str = "erd_schema.json"):
        """Export ERD schema to JSON file"""
        schema = {
            "entities": self.entities,
            "relationships": self.relationships
        }
        
        with open(filename, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"✅ ERD schema exported to {filename}")
    
    def load_from_json(self, filename: str):
        """Load ERD schema from JSON file"""
        try:
            with open(filename, 'r') as f:
                schema = json.load(f)
            
            self.G.clear()
            self.entities.clear()
            self.relationships.clear()
            
            # Load entities
            for entity_name, attributes in schema.get("entities", {}).items():
                self.add_entity(entity_name, attributes)
            
            # Load relationships
            for rel_name, rel_data in schema.get("relationships", {}).items():
                self.add_relationship(rel_name, rel_data["entities"], rel_data.get("attributes"))
            
            print(f"✅ ERD schema loaded from {filename}")
        except FileNotFoundError:
            print(f"❌ File {filename} not found.")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON format in {filename}.")
    
    def interactive_input(self):
        """Enhanced interactive mode"""
        print("\n🎯 Interactive ERD Builder")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("1. Add Entity")
            print("2. Add Relationship") 
            print("3. View Current ERD")
            print("4. Generate Visualization")
            print("5. Export to JSON")
            print("6. Load from JSON")
            print("7. Exit")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == "1":
                self._add_entity_interactive()
            elif choice == "2":
                self._add_relationship_interactive()
            elif choice == "3":
                self.view_summary()
            elif choice == "4":
                self.visualize()
            elif choice == "5":
                filename = input("Enter filename (default: erd_schema.json): ").strip() or "erd_schema.json"
                self.export_to_json(filename)
            elif choice == "6":
                filename = input("Enter filename to load: ").strip()
                if filename:
                    self.load_from_json(filename)
            elif choice == "7":
                break
            else:
                print("❌ Invalid choice. Please try again.")

    def _add_entity_interactive(self):
        """Interactive entity creation with enhanced validation"""
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
        
        # Suggest adding at least one primary key
        has_primary_key = False
        
        while True:
            attr_name = input("  Attribute name: ").strip()
            if not attr_name:
                if not attributes:
                    print("⚠️ Entity must have at least one attribute.")
                    continue
                if not has_primary_key:
                    print("⚠️ Consider adding a primary key attribute.")
                break
                
            if attr_name in existing_attr_names:
                print(f"❌ Attribute '{attr_name}' already added to this entity.")
                continue
                
            attr_type = input(f"  Type for '{attr_name}' (default: VARCHAR): ").strip() or "VARCHAR"
            is_key = input(f"  Is '{attr_name}' a primary key? (y/n): ").strip().lower() == 'y'
            is_derived = input(f"  Is '{attr_name}' derived? (y/n): ").strip().lower() == 'y'
            
            if is_key:
                has_primary_key = True
            
            attributes.append({
                "name": attr_name, 
                "type": attr_type, 
                "is_key": is_key, 
                "is_derived": is_derived
            })
            existing_attr_names.add(attr_name)

        self.add_entity(entity_name, attributes)
        print(f"✅ Added entity '{entity_name}' with {len(attributes)} attributes.")

    def _add_relationship_interactive(self):
        """Enhanced interactive relationship creation"""
        if len(self.entities) < 2:
            print("❌ You need at least two entities to create a relationship.")
            return
        
        print("\nAvailable entities:")
        entity_list = list(self.entities.keys())
        for i, entity in enumerate(entity_list, 1):
            print(f"{i}. {entity}")

        rel_name = input("\nEnter relationship name (e.g., 'WorksIn'): ").strip()
        if not rel_name:
            print("❌ Relationship name cannot be empty.")
            return
        if rel_name in self.relationships:
            print(f"❌ Relationship '{rel_name}' already exists.")
            return

        entities_in_rel = []
        print("\nSelect entities for this relationship (enter numbers, press Enter to finish):")
        while len(entities_in_rel) < 2:
            try:
                choice = input("  Entity number (or Enter to finish if ≥2 selected): ").strip()
                if not choice and len(entities_in_rel) >= 2:
                    break
                if not choice:
                    print("❌ Need at least 2 entities for a relationship.")
                    continue
                    
                idx = int(choice) - 1
                if 0 <= idx < len(entity_list):
                    entity = entity_list[idx]
                    if entity not in entities_in_rel:
                        entities_in_rel.append(entity)
                        print(f"  Added: {entity}")
                    else:
                        print(f"❌ {entity} already selected.")
                else:
                    print("❌ Invalid entity number.")
            except ValueError:
                print("❌ Please enter a valid number.")

        # Add relationship attributes
        attributes = []
        if input("\nAdd attributes to this relationship? (y/n): ").strip().lower() == 'y':
            print(f"Adding attributes for '{rel_name}' (press Enter with empty name to finish):")
            while True:
                attr_name = input("  Attribute name: ").strip()
                if not attr_name:
                    break
                attr_type = input(f"  Type for '{attr_name}' (default: VARCHAR): ").strip() or "VARCHAR"
                attributes.append({"name": attr_name, "type": attr_type})

        self.add_relationship(rel_name, entities_in_rel, attributes)
        print(f"✅ Added relationship '{rel_name}' between {entities_in_rel}.")

    def view_summary(self):
        """Enhanced summary view"""
        print("\n📋 Current ERD Summary")
        print("=" * 40)
        if not self.entities:
            print("ERD is currently empty.")
            return

        print(f"📊 Statistics: {len(self.entities)} entities, {len(self.relationships)} relationships")
        print("\n🏢 Entities:")
        for name, attrs in self.entities.items():
            primary_keys = [a for a in attrs if a.get('is_key')]
            regular_attrs = [a for a in attrs if not a.get('is_key')]
            
            print(f"  • {name}")
            if primary_keys:
                pk_str = ', '.join([f"{a['name']} ({a['type']})" for a in primary_keys])
                print(f"    🔑 Primary Keys: {pk_str}")
            if regular_attrs:
                attr_str = ', '.join([f"{a['name']} ({a['type']})" for a in regular_attrs])
                print(f"    📝 Attributes: {attr_str}")

        if self.relationships:
            print("\n🔗 Relationships:")
            for name, rel in self.relationships.items():
                entities = ' ↔ '.join(rel['entities'])
                print(f"  • {name}: {entities}")
                if rel.get('attributes'):
                    attr_strs = [f"{a['name']} ({a['type']})" for a in rel['attributes']]
                    print(f"    📋 Attributes: {', '.join(attr_strs)}")
    
    def visualize(self):
        """Enhanced visualization with better layout"""
        if not self.G.nodes():
            print("❌ No entities to visualize. Add some entities first!")
            return
        
        try:
            # Create optimized layout
            pos = nx.spring_layout(self.G, k=4, iterations=100, seed=42)
            
            # Set up the plot with better sizing
            plt.figure(figsize=(16, 12))
            plt.title("Entity-Relationship Diagram", fontsize=18, fontweight='bold', pad=20)
            
            # Enhanced color scheme
            colors = {
                'entity': '#E3F2FD',      # Light blue
                'attribute': '#E8F5E8',    # Light green  
                'relationship': '#FFF9C4'  # Light yellow
            }
            
            # Draw nodes with improved styling
            for node in self.G.nodes():
                node_data = self.G.nodes[node]
                shape = node_data.get('shape', 'box')
                node_type = node_data.get('node_type', 'entity')
                is_key = node_data.get('is_key', False)
                color = colors.get(node_type, '#F5F5F5')
                
                # Gold for primary keys, red border for derived
                if is_key:
                    color = '#FFD700'  # Gold
                
                edge_color = 'red' if node_data.get('is_derived') else 'black'
                
                if shape == "box":  # Entities
                    nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_shape="s", 
                                         node_size=5000, node_color=color, 
                                         edgecolors=edge_color, linewidths=3)
                elif shape == "oval":  # Attributes
                    nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_shape="o", 
                                         node_size=3000, node_color=color,
                                         edgecolors=edge_color, linewidths=2)
                elif shape == "diamond":  # Relationships
                    nx.draw_networkx_nodes(self.G, pos, nodelist=[node], node_shape="D", 
                                         node_size=4000, node_color=color,
                                         edgecolors=edge_color, linewidths=2)
            
            # Draw edges with different styles
            solid_edges = [(u, v) for u, v, d in self.G.edges(data=True) if d.get('style', 'solid') == 'solid']
            dotted_edges = [(u, v) for u, v, d in self.G.edges(data=True) if d.get('style') == 'dotted']
            
            if solid_edges:
                nx.draw_networkx_edges(self.G, pos, edgelist=solid_edges, edge_color="black", 
                                      arrowsize=25, arrowstyle='->', width=2)
            
            if dotted_edges:
                nx.draw_networkx_edges(self.G, pos, edgelist=dotted_edges, edge_color="red", 
                                      arrowsize=25, arrowstyle='->', width=2, style='dashed')
            
            # Enhanced labels
            labels = {}
            for node in self.G.nodes():
                node_data = self.G.nodes[node]
                if 'display_name' in node_data:
                    labels[node] = node_data['display_name']
                else:
                    labels[node] = node
            
            nx.draw_networkx_labels(self.G, pos, labels, font_size=9, font_weight='bold')
            
            # Enhanced legend
            legend_elements = [
                mpatches.Patch(color='#E3F2FD', label='Entity'),
                mpatches.Patch(color='#E8F5E8', label='Attribute'), 
                mpatches.Patch(color='#FFF9C4', label='Relationship'),
                mpatches.Patch(color='#FFD700', label='Primary Key'),
                plt.Line2D([0], [0], color='red', linestyle='--', label='Derived Attribute')
            ]
            
            plt.legend(handles=legend_elements, loc='upper right', fontsize=12)
            
            plt.axis('off')
            plt.tight_layout()
            plt.savefig('erd_diagram.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("✅ ERD Visualization Complete! Saved as 'erd_diagram.png'")
            
        except Exception as e:
            print(f"❌ Visualization error: {e}")
            print("💡 Try installing required packages or check display settings.")

def main():
    """Enhanced main function with better UX"""
    print("🎨 Welcome to Advanced ERD Generator v2.0")
    print("=" * 50)
    
    erd = ERDGenerator()
    
    while True:
        print("\n🎯 Choose your mode:")
        print("1. 🎮 Interactive Mode (Manual Input)")
        print("2. 🤖 AI Generation from Topic")  
        print("3. 🎭 Demo Mode (Library System)")
        print("4. 📁 Load Existing ERD")
        print("5. ❓ Help & Tips")
        print("6. 👋 Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            erd.interactive_input()
        elif choice == "2":
            print("\n🤖 AI Topic Generator")
            print("Available domains: library, ecommerce, school, hospital")
            topic = input("Enter topic for AI generation: ").strip()
            if topic:
                erd.generate_from_ai(topic)
                if erd.entities:
                    erd.view_summary()
                    if input("\nVisualize now? (y/n): ").strip().lower() == 'y':
                        erd.visualize()
            else:
                print("❌ Topic cannot be empty.")
        elif choice == "3":
            print("🎭 Loading demo: Library Management System...")
            erd.generate_from_ai("library")
            erd.view_summary()
            erd.visualize()
        elif choice == "4":
            filename = input("Enter JSON filename to load: ").strip()
            if filename:
                erd.load_from_json(filename)
        elif choice == "5":
            print("\n💡 Help & Tips:")
            print("- Use descriptive entity and relationship names")
            print("- Always include primary keys for entities")
            print("- Relationship attributes store data about the relationship itself")
            print("- Export/import JSON files to save your work")
            print("- Try AI generation with keywords like 'hospital', 'school', etc.")
        elif choice == "6":
            print("\n🎉 Thanks for using ERD Generator!")
            print("Your diagrams have been saved. Goodbye! 👋")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
