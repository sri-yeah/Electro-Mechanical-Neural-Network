from sympy import simplify_logic, Xor, And, Or, Not
from sympy.logic.boolalg import truth_table
from sympy.abc import a, b

# user_input = input("Enter a logic expression using 'a' and 'b': ")

def get_weights(user_input):
  try:
      expr = eval(user_input, {'A': a, 'B': b, '^': Xor, '&': And, '|': Or, '~': Not})
      simplified = simplify_logic(expr)
      print('Simplified logic expression: ' + str(simplified))
      # Generate truth table
      truth_str = ''.join('1' if val else '0' for _, val in truth_table(expr, [a, b]))
      print('Truth table outputs: '+ str(truth_str))
  except:
      print("Invalid input")


  weights_dict = {0: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],          # 0000 : LOW
                  1: [0.5, 0.5, 0.0, 0.0, -0.3, 0.0, 1.0, 0.0],         # 0001 : AND
                  2: [1.0, 0.0, 0.5, 0.5, 0.0, -0.3, 1.0, -1.0],        # 0010 : A - AND
                  3: [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],          # 0011 : A
                  4: [0.0, 1.0, 0.5, 0.5, 0.0, -0.3, 1.0, -1.0],        # 0100 : B - AND
                  5: [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],          # 0101 : B
                  6: [1.0, 1.0, 0.5, 0.5, 0.0, -0.3, 1.0, -1.0],        # 0110 : XOR (OR - AND)
                  7: [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],          # 0111 : OR
                  8: [-1.0, -1.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0],        # 1000 : NOR
                  9: [0.5, 0.5, -1.0, -1.0, -0.3, 1.0, 1.0, 1.0],       # 1001 : NXOR (AND + NOR)
                  10: [0.0, -1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],        # 1010 : NOT B
                  11: [0.0, -1.0, 0.5, 0.5, 0.0, -0.3, 1.0, 1.0],       # 1011 : NOT B + AND
                  12: [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0],        # 1100 : NOT A
                  13: [-1.0, 0.0, 0.5, 0.5, 0.0, -0.3, 1.0, 1.0],       # 1101 : NOT A + AND
                  14: [0.5, 0.5, 0.0, 0.0, -0.3, 0.0, -1.0, 0.0],       # 1110 : NAND
                  15: [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0],         # 1111 : HIGH
                  }

  # Load preset weights
  output_case = '0b' + truth_str
  net_presets = weights_dict[int(output_case, 2)]
  # fc1_weights = net_presets[0]
  # fc1_bias = net_presets[1]
  # fc2_weights = net_presets[2]

  return net_presets
