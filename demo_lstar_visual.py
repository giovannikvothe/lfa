"""
Giovanni Almeida Dutra - 202465035AC
Hugo Nogueira Carvalho - 
Script de Demonstração Visual do Algoritmo L*
Mostra o passo a passo do aprendizado de forma visual e interativa
"""

import sys
import os
import time

# Adiciona o diretório lstar ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lstar'))

from lstar.learn import _learn_dfa
from lstar import iterative_deeping_ce
from functools import lru_cache

def print_separator(title="", char="=", width=70):
    if title:
        print("\n" + char * width)
        print(title.center(width))
        print(char * width)
    else:
        print(char * width)

def format_word(word):
    if not word:
        return "ε"
    return "".join(map(str, word))

def visualize_dfa(dfa, max_states=10):
    states = list(dfa.states())
    num_states = len(states)
    
    if num_states > max_states:
        print(f"DFA com {num_states} estados (demais para visualizar)")
        return
    
    print(f"Estrutura do DFA ({num_states} estados):")
    
    # Mostrar estados e quais são de aceitação
    print("Estados:")
    for state in sorted(states, key=lambda x: (len(str(x)), str(x))):
        label = dfa.label(state)
        marker = "✓" if label else "✗"
        state_str = format_word(state)
        print(f"{marker} {state_str}")
    
    # Mostrar transições
    print("Transições:")
    shown_transitions = set()
    
    try:
        # Estratégia: descobrir transições testando palavras curtas
        # Começar com palavras de 1 símbolo (transições do estado inicial)
        # Depois tentar palavras de 2 símbolos para descobrir mais transições
        
        max_transitions_to_show = min(num_states * 2, 10)  # Limitar número de transições mostradas
        
        # Primeiro: transições do estado inicial (palavras de 1 símbolo)
        for inp in sorted(dfa.inputs):
            word = (inp,)
            trace = list(dfa.trace(word))
            if len(trace) >= 2:
                from_state = trace[0]
                to_state = trace[-1]
                if (from_state, inp) not in shown_transitions:
                    from_str = format_word(from_state)
                    to_str = format_word(to_state)
                    print(f"{from_str:8} --[{inp}]--> {to_str:8}")
                    shown_transitions.add((from_state, inp))
                    if len(shown_transitions) >= max_transitions_to_show:
                        return
        
        # Segundo: tentar descobrir mais transições testando palavras de 2 símbolos
        if len(shown_transitions) < max_transitions_to_show:
            for inp1 in sorted(dfa.inputs):
                for inp2 in sorted(dfa.inputs):
                    word = (inp1, inp2)
                    trace = list(dfa.trace(word))
                    if len(trace) >= 3:
                        # Pegar a transição do segundo símbolo (penúltimo -> último)
                        from_state = trace[-2] if len(trace) >= 2 else trace[0]
                        to_state = trace[-1]
                        if (from_state, inp2) not in shown_transitions:
                            from_str = format_word(from_state)
                            to_str = format_word(to_state)
                            print(f"{from_str:8} --[{inp2}]--> {to_str:8}")
                            shown_transitions.add((from_state, inp2))
                            if len(shown_transitions) >= max_transitions_to_show:
                                return
        
        # Terceiro: se ainda não mostramos muitas, testar mais combinações
        if len(shown_transitions) < max_transitions_to_show and num_states <= 4:
            # Para DFAs pequenos, testar palavras de 3 símbolos
            for inp1 in sorted(dfa.inputs):
                for inp2 in sorted(dfa.inputs):
                    for inp3 in sorted(dfa.inputs):
                        word = (inp1, inp2, inp3)
                        trace = list(dfa.trace(word))
                        if len(trace) >= 4:
                            from_state = trace[-2]
                            to_state = trace[-1]
                            if (from_state, inp3) not in shown_transitions:
                                from_str = format_word(from_state)
                                to_str = format_word(to_state)
                                print(f"{from_str:8} --[{inp3}]--> {to_str:8}")
                                shown_transitions.add((from_state, inp3))
                                if len(shown_transitions) >= max_transitions_to_show:
                                    return
        
        # Se não descobrimos transições suficientes, informar
        if not shown_transitions:
            print("(testando transições...)")
            
    except Exception as e:
        pass

def demonstrate_learning_with_steps(inputs, label_func, label_name, depth=10, test_cases=None, outputs=None):
    print_separator(f"APRENDIZADO: {label_name}", "=", 80)
    
    print(f"\nLinguagem: {label_name}")
    print(f"Alfabeto: {inputs}")
    
    # Mostrar alguns exemplos da função
    print("\nExemplos de Membership Queries:")
    example_words = [(), (0,), (1,), (0, 1), (1, 1), (1, 1, 1), (1, 1, 1, 1)]
    for word in example_words:
        result = label_func(word)
        word_str = format_word(word)

        if isinstance(result, bool):
            marker = "✓" if result else "✗"
            print(f"{marker} label({word_str:12}) = {result}")
        else:
            print(f"→ label({word_str:12}) = {result}")
    
    print("\n" + "─" * 80)
    print("INICIANDO APRENDIZADO COM ALGORITMO L*")
    print("─" * 80)
    
    # Usar _learn_dfa para ver cada iteração
    iteration = 0
    dfa_final = None
    try:
        hypotheses = _learn_dfa(inputs, label_func, iterative_deeping_ce(label_func, depth=depth), outputs)
        
        for dfa in hypotheses:
            iteration += 1
            dfa_final = dfa  # Guardar o último DFA
            
            print(f"\n{'='*80}")
            print(f"ITERAÇÃO {iteration}")
            print(f"{'='*80}")
            
            if iteration == 1:
                print("Hipótese inicial - pode conter erros")
                print("O algoritmo vai usar os erros(contra-exemplos) para refinar a hipótese.")
            
            num_states = len(dfa.states())
            print(f"Hipótese {iteration}: DFA com {num_states} estado(s)")
            
            # Visualizar DFA
            visualize_dfa(dfa)
            
            # Testar alguns casos
            print(f"\nTestando algumas palavras:")
            test_words = [(), (1,), (1, 1), (1, 1, 1), (1, 1, 1, 1)]
            for word in test_words:
                result = dfa.label(word)
                expected = label_func(word)
                word_str = format_word(word)
                match = "✓" if result == expected else "✗"
                if result == expected:
                    status = "CORRETO"
                    print(f"{match} {word_str:12} -> {result} (esperado: {expected}) [{status}]")
                else:
                    status = "DIVERGÊNCIA"
                    print(f"{match} {word_str:12} -> {result} (esperado: {expected}) [{status}]")
        
        # Última hipótese, dfa_final já é o correto
        print(f"\n{'='*80}")
        print(f"CONVERGÊNCIA ALCANÇADA - ITERAÇÃO {iteration}")
        print(f"{'='*80}")
        
        if dfa_final is None:
            # Se não houve iterações, criar o DFA inicial
            from lstar import learn_dfa
            dfa_final = learn_dfa(inputs, label_func, iterative_deeping_ce(label_func, depth=depth), outputs)
        
        num_states = len(dfa_final.states())
        print(f"DFA Final: {num_states} estado(s)")
        
        visualize_dfa(dfa_final)
        
        # Validação completa
        if test_cases:
            print(f"\n{'─'*80}")
            print("VALIDAÇÃO FINAL")
            print(f"{'─'*80}")
            all_passed = True
            for word, expected in test_cases:
                result = dfa_final.label(word)
                word_str = format_word(word)
                match = "✓" if result == expected else "✗"
                if result != expected:
                    all_passed = False
                
                result_str = str(result)
                expected_str = str(expected)
                print(f"{match} {word_str:15} -> {result_str:5} (esperado: {expected_str:5})")
            
            if all_passed:
                print("TODOS OS TESTES PASSARAM!")
            else:
                print("ALGUNS TESTES FALHARAM!")
        
        return dfa_final
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print_separator("DEMONSTRAÇÃO VISUAL DO ALGORITMO L*", "=", 80)
    print_separator("Aprendizado de Autômatos Finitos", "=", 80)
    
    # ============================================================================
    # TESTE 1: Múltiplos de 4
    # ============================================================================
    @lru_cache(maxsize=None)
    def is_mult_4(word):
        return (sum(word) % 4) == 0
    
    test_cases_1 = [
        ((), True),
        ((1,), False),
        ((1, 1,), False),
        ((1, 1, 1), False),
        ((1, 1, 1, 1), True),
        ((1, 1, 0, 1), False),
        ((0, 1, 1, 1, 1), True),
    ]
    
    dfa1 = demonstrate_learning_with_steps(
        inputs={0, 1},
        label_func=is_mult_4,
        label_name="Múltiplos de 4 (número de 1's % 4 == 0)",
        depth=10,
        test_cases=test_cases_1
    )
    
    input("\nPressione ENTER para continuar com o próximo teste...")
    
    # ============================================================================
    # TESTE 2: Moore Machine
    # ============================================================================
    print("\n\n")
    def sum_mod_4(word):
        return sum(word) % 4
    
    test_cases_2 = [
        ((), 0),
        ((1,), 1),
        ((1, 1,), 2),
        ((1, 1, 1), 3),
        ((1, 1, 1, 1), 0),
    ]
    
    dfa2 = demonstrate_learning_with_steps(
        inputs={0, 1},
        label_func=sum_mod_4,
        label_name="Moore Machine: Soma módulo 4",
        depth=8,
        test_cases=test_cases_2,
        outputs={0, 1, 2, 3}
    )
    
    input("\nPressione ENTER para continuar com o último teste...")
    
    # ============================================================================
    # TESTE 3: Número Par de 1's
    # ============================================================================
    print("\n\n")
    @lru_cache(maxsize=None)
    def even_ones(word):
        return (word.count(1) % 2) == 0
    
    test_cases_3 = [
        ((), True),
        ((1,), False),
        ((1, 1,), True),
        ((1, 1, 1), False),
        ((0, 1, 0, 1), True),
    ]
    
    dfa3 = demonstrate_learning_with_steps(
        inputs={0, 1},
        label_func=even_ones,
        label_name="Número Par de 1's",
        depth=8,
        test_cases=test_cases_3
    )
    
    # ============================================================================
    # RESUMO
    # ============================================================================
    print_separator("RESUMO DA DEMONSTRAÇÃO", "=", 80)
    
    print("\nResultados:")
    print(f"✓ TESTE 1 (Múltiplos de 4):      {len(dfa1.states()) if dfa1 else 0} estados")
    print(f"✓ TESTE 2 (Moore Machine):       {len(dfa2.states()) if dfa2 else 0} estados")
    print(f"✓ TESTE 3 (Número Par):          {len(dfa3.states()) if dfa3 else 0} estados")
    
    print_separator("DEMONSTRAÇÃO CONCLUÍDA!", "=", 80)

if __name__ == "__main__":
    main()
