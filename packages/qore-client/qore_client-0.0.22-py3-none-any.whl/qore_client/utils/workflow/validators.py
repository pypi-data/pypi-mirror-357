from typing import List, Set

from .models import Edge, Node


class WorkflowValidator:
    @staticmethod
    def validate_node_exists(node_id: str, nodes: List[Node]) -> None:
        is_exists = any(node.id == node_id for node in nodes)
        if not is_exists:
            raise ValueError(f"Node with id {node_id} not found")

    @staticmethod
    def validate_node_can_be_deleted(node_id: str) -> None:
        if node_id in ["start-node", "end-node"]:
            raise ValueError(f"Cannot delete {node_id}")

    @staticmethod
    def validate_edges(edges: List[Edge], node_ids: Set[str]) -> List[Edge]:
        valid_edges = []
        for edge in edges:
            if edge.source in node_ids and edge.target in node_ids:
                valid_edges.append(edge)
        return valid_edges

    @staticmethod
    def validate_node_connections(edges: List[Edge], node_ids: Set[str]) -> bool:
        for edge in edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                return False
        return True
