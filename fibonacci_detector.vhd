library ieee;
use ieee.std_logic_1164.all;
library work;
use work.Gates.all;
entity fibonacci_detector is
port(x4, x3, x2, x1, x0: in std_logic; output: out std_logic );
end fibonacci_detector;
Architecture struct of fibonacci_detector is
Signal s1, s2, s3, s4, s5,s6, s7, s8, s9, s10,s11, s12, s13, s14, s15,s16: std_logic;
Begin 
g1: INVERTER port map (x4, s1);
g2: AND_2 port map (s1, s2, s3);
g3: AND_2 port map (s3, s4, s5);
g4: INVERTER port map (x3, s2);
g5: INVERTER port map (x2, s4);
g6: OR_2 port map (s5, s10, s16);
g7: INVERTER port map (x3, s6);
g8: AND_2 port map (s6, x2, s7);
g9: AND_2 port map (s7, s9, s10);
g10: INVERTER port map (x1, s8);
g11: AND_2 port map (s8, x0, s9);
g12: INVERTER port map (x4, s11);
g13: AND_2 port map (s11, s12, s13);
g14: INVERTER port map (x1, s12);
g15: AND_2 port map (s13, s14, s15);
g16: XNOR_2 port map (x2, x0, s14);
g17: OR_2 port map (s16, s15, output);
end struct;