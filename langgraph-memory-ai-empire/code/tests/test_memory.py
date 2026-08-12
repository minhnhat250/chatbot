from uuid import uuid4

from langgraph.store.memory import InMemoryStore

from chat_service import ChatService
from long_term_memory import load_profile, save_profile
from short_term_memory import ask, build_graph


def test_two_threads_do_not_mix_names():
    graph = build_graph()
    thread_a = str(uuid4())
    thread_b = str(uuid4())

    ask(graph, thread_a, "T\u00f4i t\u00ean Nh\u1eadt.")
    ask(graph, thread_b, "T\u00f4i t\u00ean An.")

    assert ask(graph, thread_a, "T\u00f4i t\u00ean g\u00ec?") == "B\u1ea1n t\u00ean Nh\u1eadt."
    assert ask(graph, thread_b, "T\u00f4i t\u00ean g\u00ec?") == "B\u1ea1n t\u00ean An."


def test_profile_is_separated_by_user_id():
    store = InMemoryStore()
    save_profile(store, "user-a", {"name": "Nh\u1eadt"})
    save_profile(store, "user-b", {"name": "An"})

    assert load_profile(store, "user-a")["name"] == "Nh\u1eadt"
    assert load_profile(store, "user-b")["name"] == "An"


def test_long_term_memory_crosses_threads_for_same_user():
    service = ChatService()
    service.ask(
        user_id="user-nhat",
        thread_id=str(uuid4()),
        message="H\u00e3y nh\u1edb t\u00f4i t\u00ean l\u00e0 Nh\u1eadt.",
    )

    answer = service.ask(
        user_id="user-nhat",
        thread_id=str(uuid4()),
        message="T\u00f4i t\u00ean g\u00ec?",
    )
    assert answer == "B\u1ea1n t\u00ean Nh\u1eadt."


def test_long_term_memory_does_not_cross_users():
    service = ChatService()
    service.ask(
        user_id="user-a",
        thread_id=str(uuid4()),
        message="H\u00e3y nh\u1edb t\u00f4i t\u00ean l\u00e0 Nh\u1eadt.",
    )

    answer = service.ask(
        user_id="user-b",
        thread_id=str(uuid4()),
        message="T\u00f4i t\u00ean g\u00ec?",
    )
    assert answer == "T\u00f4i ch\u01b0a bi\u1ebft t\u00ean b\u1ea1n."
