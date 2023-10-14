import json


LAMBDA = "Lambda"
QT = "qt"


class State:
    def __init__(
        self,
        name: str,
        is_final: bool=False,
        moves: list=[]
    ) -> None:
        self.name = name
        self.is_final = is_final
        self.moves = moves

    def __str__(self):
        result = "<<" if self.is_final else "<"
        result += self.name
        result += ">>\n" if self.is_final else ">\n"
        if len(self.moves) == 0:
            result += "no moves!"
        for move in self.moves:
            result += str(move) + "  "
        return result


class Move:
    def __init__(
        self,
        by: str,
        to_state: str
    ) -> None:
        self.by = str(by)
        self.to_state = to_state


    def __str__(self) -> str:
        return self.by + "->" + self.to_state

    
    def __eq__(self, __o: object) -> bool:
        return type(__o) == Move and self.by == __o.by  and self.to_state == __o.to_state


class XFA:
    def __init__(
        self,
        start_state_name: str,
        states: list=[],
        sigma: list=[]
    ) -> None:
        self.start_state_name = start_state_name
        self.states = states
        self.sigma = sigma


    def __str__(self) -> str:
        result = f"sigma={self.sigma}\n"
        result += f"start state={self.start_state_name}\n"
        for state in self.states:
            result += "-" * 80 + "\n"
            result += str(state) + "\n"
        return result


    def add_state(
        self,
        state: State
    ):
        self.states.append(state)


    def get_start_state(self) -> State:
        for state in self.states:
            if state.name == self.start_state_name:
                return state
        return None


class NFA(XFA):
    def __str__(self) -> str:
        return "=" * 80 + "\nNFA:\n" + super().__str__() + "=" * 80


    def to_dfa(self):
        qt = State(
            name=QT,
            is_final=False,
            moves=[Move(by=terminal, to_state=QT) for terminal in self.sigma]
        )
        delta_table = {}
        for nfa_state in self.states:
            delta_table[nfa_state.name] = {}
            for terminal in self.sigma:
                delta_table[nfa_state.name][terminal] = []
            for move in nfa_state.moves:
                if move.by != LAMBDA:
                    delta_table[nfa_state.name][move.by].append(move.to_state)
                else:
                    for state in self.states:
                        if state.name == move.to_state:
                            for move2 in state.moves:
                                delta_table[nfa_state.name][move2.by].append(move2.to_state)
                    for move2 in nfa_state.moves:
                        if move2.by != LAMBDA:
                            delta_table[nfa_state.name][move2.by].append(move.to_state)
        for nfa_state in self.states:
            for terminal in self.sigma:
                if len(delta_table[nfa_state.name][terminal]) == 0:
                    delta_table[nfa_state.name][terminal] = [qt.name]

        dfa = DFA(
            start_state_name=self.start_state_name,
            sigma=self.sigma
        )
        nfa_start_state = self.get_start_state()
        dfa_start_state = State(
            name=nfa_start_state.name,
            is_final=nfa_start_state.is_final
        )
        dfa_start_state.moves = NFA._get_dfa_moves_from_delta_table([dfa_start_state], delta_table, nfa.sigma)
        dfa.add_state(dfa_start_state)
        for state in dfa.states:
            for move in state.moves:
                if move.to_state != QT and move.to_state not in [state.name for state in dfa.states]:
                    if "[" in move.to_state:
                        new_states_name_list = json.loads(move.to_state)
                    else:
                        new_states_name_list = [move.to_state]
                    new_state_list = []
                    for item in self.states:
                        if item.name in new_states_name_list:
                            new_state_list.append(item)
                    is_final = False
                    for item in new_states_name_list:
                        for item2 in self.states:
                            if item == item2.name and item2.is_final:
                                is_final = True
                    new_state = State(
                        name=move.to_state,
                        is_final=is_final,
                        moves=NFA._get_dfa_moves_from_delta_table(new_state_list, delta_table, nfa.sigma)
                    )
                    dfa.add_state(new_state)
        if dfa.need_qt_state():
            dfa.add_state(qt)
        return dfa
    

    def _get_dfa_moves_from_delta_table(state_list: list, delta_table: dict, sigma: list):
        moves_list = []
        for state in state_list:
            for terminal in delta_table[state.name]:
                if len(delta_table[state.name][terminal]) > 1:
                    to_state = json.dumps(delta_table[state.name][terminal], sort_keys=True)
                else:
                    to_state = delta_table[state.name][terminal][0]
                if to_state != QT:
                    moves_list.append(
                        Move(
                            by=terminal,
                            to_state=to_state
                        )
                    )
        index1 = 0
        while index1 < len(moves_list):
            index2 = index1 + 1
            while index2 < len(moves_list):
                if moves_list[index1] == moves_list[index2]:
                    del moves_list[index2]
                    continue
                index2 += 1
            index1 += 1
        for terminal in sigma:
            if terminal not in [t.by for t in moves_list]:
                moves_list.append(
                    Move(
                        by=terminal,
                        to_state=QT
                    )
                )
        return moves_list


class DFA(XFA):
    def __str__(self) -> str:
        return "=" * 80 + "\nDFA:\n" + super().__str__() + "=" * 80


    def need_qt_state(self):
        for state in self.states:
            for move in state.moves:
                if move.to_state == QT:
                    return True
        return False


if __name__ == "__main__":
    q0 = State(
        name="q0",
        is_final=False,
        moves=[
            Move(by="a", to_state="q0"),
            Move(by="a", to_state="q1"),
            Move(by="a", to_state="q2")
        ]
    )
    q1 = State(
        name="q1",
        is_final=True,
        moves=[
            Move(by="b", to_state="q1")
        ]
    )
    q2 = State(
        name="q2",
        is_final=False,
        moves=[
            Move(by=LAMBDA, to_state="q1"),
            Move(by="c", to_state="q2")
        ]
    )
    nfa = NFA(
        start_state_name="q0",
        states=[q0,q1,q2],
        sigma=["a","b","c"]
    )
    print(nfa)
    print(nfa.to_dfa())


# if __name__ == "__main__":
#     q1 = State(
#         name="q1",
#         is_final=False,
#         moves=[
#             Move(by="a", to_state="q1"),
#             Move(by=LAMBDA, to_state="q2"),
#             Move(by=LAMBDA, to_state="q3")
#         ]
#     )
#     q2 = State(
#         name="q2",
#         is_final=False,
#         moves=[
#             Move(by="b", to_state="q2"),
#             Move(by="b", to_state="q4")
#         ]
#     )
#     q3 = State(
#         name="q3",
#         is_final=False,
#         moves=[
#             Move(by="c", to_state="q3"),
#             Move(by="c", to_state="q4")
#         ]
#     )
#     q4 = State(
#         name="q4",
#         is_final=True
#     )
#     nfa = NFA(
#         start_state_name="q1",
#         states=[q1,q2,q3,q4],
#         sigma=["a","b","c"]
#     )
#     print(nfa)
#     print(nfa.to_dfa())