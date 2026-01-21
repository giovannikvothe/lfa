"""
Giovanni Almeida Dutra - 202465035AC
Hugo Nogueira Carvalho - 202065251AC
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
from dfa import dfa2dict

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
    """
    Mostra TODAS as transições do DFA (não mais apenas uma amostra).

    Observação: para evitar poluir demais a tela, se o número de estados
    for maior que `max_states`, apenas avisamos e não listamos tudo.
    """
    states = list(dfa.states())
    num_states = len(states)

    if num_states > max_states:
        print(f"DFA com {num_states} estados (demais para visualizar todas as transições)")
        return

    print(f"Estrutura do DFA ({num_states} estados):")

    # Mostrar estados e quais são de aceitação
    print("Estados:")
    sorted_states = sorted(states, key=lambda x: (len(str(x)), str(x)))
    for state in sorted_states:
        label = dfa.label(state)
        marker = "✓" if label else "✗"
        state_str = format_word(state)
        print(f"{marker} {state_str}")

    # Mostrar TODAS as transições (estado, símbolo) -> próximo estado
    print("Transições (completas):")
    
    # Coletar todas as transições de forma sistemática
    all_transitions = []
    for state in sorted_states:
        from_str = format_word(state)
        for inp in sorted(dfa.inputs):
            try:
                # Tentar usar o método transition diretamente
                to_state = None
                if hasattr(dfa, 'transition'):
                    try:
                        to_state = dfa.transition(state, inp)
                    except:
                        pass
                
                # Se transition não funcionou, usar trace
                if to_state is None:
                    try:
                        word_from_state = state + (inp,)
                        trace = list(dfa.trace(word_from_state))
                        if trace:
                            to_state = trace[-1]
                    except:
                        pass
                
                # Se ainda não temos o estado, tentar usar dfa2dict
                if to_state is None:
                    try:
                        dfa_dict = dfa2dict(dfa)
                        # dfa2dict retorna (start, inputs, transitions, outputs, label)
                        # transitions é um dict: {state: {symbol: next_state}}
                        if len(dfa_dict) >= 3:
                            transitions_dict = dfa_dict[2]
                            if state in transitions_dict and inp in transitions_dict[state]:
                                to_state = transitions_dict[state][inp]
                    except:
                        pass
                
                if to_state is not None:
                    to_str = format_word(to_state)
                    all_transitions.append((from_str, inp, to_str))
                else:
                    print(f"{from_str:8} --[{inp}]--> (não encontrado)")
            except Exception as e:
                print(f"{from_str:8} --[{inp}]--> (erro: {type(e).__name__})")
    
    # Imprimir todas as transições encontradas, ordenadas
    for from_str, inp, to_str in sorted(all_transitions):
        print(f"{from_str:8} --[{inp}]--> {to_str:8}")

def demonstrate_learning_with_steps(inputs, label_func, label_name, depth=10, test_cases=None, outputs=None):
    print_separator(f"APRENDIZADO: {label_name}", "=", 80)
    
    print(f"\nLinguagem: {label_name}")
    print(f"Alfabeto: {inputs}")
    
    # Mostrar alguns exemplos da função
    print("\nExemplos de Membership Queries:")

    # Conjunto padrão de exemplos
    example_words = [
        (),            # palavra vazia
        (0,), (1,),
        (1, 0), (0, 1),
        (1, 1),
        (1, 1, 1),
        (1, 1, 1, 1),
    ]

    # Ajustar exemplos quando a linguagem é "múltiplos de 4"
    if "múltiplos de 4" in label_name.lower():
        example_words = [
            (),                         # 0 uns  -> múltiplo de 4
            (1,),                       # 1 um   -> não
            (1, 1),                     # 2 uns  -> não
            (1, 1, 1),                  # 3 uns  -> não
            (1, 1, 1, 1),               # 4 uns  -> sim
            (0, 1, 1, 1, 1),            # 4 uns espalhados -> sim
            (1, 1, 0, 1),               # 3 uns -> não
            (1, 1, 1, 1, 1),            # 5 uns -> não
        ]
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

            # Conjunto padrão de testes
            test_words = [
                (),                 # vazia
                (1,),
                (1, 1),
                (1, 1, 1),
                (1, 1, 1, 1),
                (1, 0, 1),
                (0, 1, 1),
                (1, 1, 0, 1),
            ]

            # Ajustar testes para o caso de múltiplos de 4
            if "múltiplos de 4" in label_name.lower():
                test_words = [
                    (),                         
                    (1,),                       
                    (1, 1,),                    
                    (1, 1, 1),                  
                    (1, 1, 1, 1),               
                    (1, 1, 1, 1, 1),           
                    (1, 1, 1, 1, 1, 1, 1, 1),   
                    (0, 1, 1, 1, 1),           
                    (1, 1, 0, 1),               
                    (1, 0, 1, 0, 1, 1),         
                ]

            # Cabeçalho mais legível
            print(f"{'palavra':12} | {'#1s':>3} | {'label real':>10} | {'DFA':>5} | status")
            print("-" * 60)

            for word in test_words:
                result = dfa.label(word)
                expected = label_func(word)
                word_str = format_word(word)

                # número de 1s (útil para múltiplos de 4)
                ones_count = word.count(1)

                match = "✓" if result == expected else "✗"
                status = "CORRETO" if result == expected else "DIVERGÊNCIA"

                print(
                    f"{word_str:12} | {ones_count:>3} | "
                    f"{str(expected):>10} | {str(result):>5} | {status}"
                )
        
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
                print("\nTODOS OS TESTES PASSARAM!")
            else:
                print("\nALGUNS TESTES FALHARAM!")
        
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
    # TESTE 1: Número Par de 1's
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

    input("\nPressione ENTER para continuar com o próximo teste...")

    # ============================================================================
    # TESTE 2: Múltiplos de 4
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
    # TESTE 3: Moore Machine
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
    
    input("\nPressione ENTER para ver o resumo...")
    
    # ============================================================================
    # RESUMO
    # ============================================================================
    print_separator("RESUMO DA DEMONSTRAÇÃO", "=", 80)
    
    print("\nResultados:")
    print(f"✓ TESTE 1 (Número Par):          {len(dfa3.states()) if dfa3 else 0} estados")
    print(f"✓ TESTE 2 (Múltiplos de 4):      {len(dfa1.states()) if dfa1 else 0} estados")
    print(f"✓ TESTE 3 (Moore Machine):       {len(dfa2.states()) if dfa2 else 0} estados")
    
    print_separator("DEMONSTRAÇÃO CONCLUÍDA!", "=", 80)

if __name__ == "__main__":
    main()
