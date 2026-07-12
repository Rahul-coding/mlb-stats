import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from pathlib import Path
import tempfile
from trade_trees.data_loader import load_and_build_tree

def render_trade_trees():
    # Clean Dark Slate styling
    st.markdown("""
        <style>
        body, .stApp { background-color: #1a1e1e; color: #e0e0e0; }
        h1 { color: #8fa89b !important; font-family: 'Arial', sans-serif; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🌿 Dynamic Trade Tree Visualizer")

    csv_path = Path(__file__).resolve().parent / "mlb_trades.csv"
    relationship_df, all_players = load_and_build_tree(str(csv_path))

    if all_players:
        st.sidebar.header("Tree Customization")
        max_generations = st.sidebar.slider(
            "Max Depth (Generations Away)", 
            min_value=1, 
            max_value=5, 
            value=2,
            help="How many generation steps out the tree should expand."
        )

        selected_player = st.selectbox("Type or select ANY player from your CSV:", all_players)

        # Build network topology
        G_master = nx.DiGraph()
        for _, row in relationship_df.iterrows():
            G_master.add_edge(row['parent_player'], row['player'], date=row['date'], label=row['date'])

        if selected_player in G_master:
            # 1. Bounded extraction using NetworkX BFS to trace specific links
            G_reversed = G_master.reverse(copy=False)
            upstream_nodes = set(nx.bfs_tree(G_reversed, source=selected_player, depth_limit=max_generations).nodes)
            downstream_nodes = set(nx.bfs_tree(G_master, source=selected_player, depth_limit=max_generations).nodes)

            connected_nodes = upstream_nodes.union(downstream_nodes).union({selected_player})
            sub_graph = G_master.subgraph(connected_nodes).copy()
            
            # --- THE GENERATION LEVEL FIX ---
            # Instead of grouping by raw calendar dates, we calculate steps away from our selected focus player.
            node_levels = {}
            
            # We find the global minimum/offset so that the absolute oldest ancestor sits at level 0.
            raw_distances = {}
            for node in sub_graph.nodes:
                if node == selected_player:
                    raw_distances[node] = 0
                elif node in upstream_nodes:
                    # Ancestors are placed in generations BEFORE (-1, -2, etc.)
                    path_len = nx.shortest_path_length(sub_graph, source=node, target=selected_player)
                    raw_distances[node] = -path_len
                elif node in downstream_nodes:
                    # Descendants are placed in generations AFTER (1, 2, etc.)
                    path_len = nx.shortest_path_length(sub_graph, source=selected_player, target=node)
                    raw_distances[node] = path_len
                else:
                    raw_distances[node] = 0

            # Shift all numbers into positive integers so Vis.js can read them starting at level 0
            min_distance = min(raw_distances.values()) if raw_distances else 0
            for node, dist in raw_distances.items():
                node_levels[node] = dist - min_distance

            # Setup canvas
            net = Network(notebook=False, directed=True, height="700px", width="100%", bgcolor="#1a1e1e", font_color="#e0e0e0")
            
            # Add styled nodes sorted by chronological tier
            for node in sub_graph.nodes:
                is_target = (node == selected_player)
                color = "#c29180" if is_target else "#364a45"
                border = "#d9ab9a" if is_target else "#4e6660"
                
                net.add_node(
                    node, 
                    label=node, 
                    shape="box",
                    level=int(node_levels.get(node, 0)), # <--- Strictly maps your generation slots!
                    color={"background": color, "border": border},
                    font={"size": 13, "color": "#e2e8f0"},
                    margin=12, 
                    borderWidth=1.5
                )

            # Connect edges (Omit labels so dates stay hidden)
            for source, target in sub_graph.edges():
                net.add_edge(source, target, color="#556361")

            # Explicit configuration rules to render your top-down flow perfectly
            hierarchical_options = """
            var options = {
              "edges": {
                "arrows": { "to": { "enabled": true, "scaleFactor": 0.5 } },
                "smooth": { "type": "cubicBezier", "forceDirection": "vertical", "roundness": 0.4 }
              },
              "layout": {
                "hierarchical": {
                  "enabled": true,
                  "levelSeparation": 150,
                  "nodeSpacing": 250,
                  "treeSpacing": 300,
                  "blockShifting": true,
                  "edgeMinimization": true,
                  "parentCentralization": true,
                  "direction": "UD",
                  "sortMethod": "layout"
                }
              },
              "physics": { "enabled": false }
            }
            """
            net.set_options(hierarchical_options)

            # Write outside the workspace so Streamlit file watching does not trigger rerun loops.
            output_path = Path(tempfile.gettempdir()) / "mlb_trade_trees_dynamic_output.html"
            net.write_html(str(output_path))
            with open(output_path, 'r', encoding='utf-8') as f:
                html_data = f.read()
            components.html(html_data, height=720)
        else:
            st.info(f"Player '{selected_player}' has no associated exchange lines in this dataset.")
    else:
        st.warning("Please verify your 'mlb_trades.csv' contains data.")


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Dynamic Trade Tree Visualizer")
    render_trade_trees()