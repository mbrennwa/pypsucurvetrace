###############################
# Constants and control flags #
###############################


PROGRAM_NAME                      = 'PyPSU Curvetrace'
PROGRAM_VERSION                   = 'DEVELOPMENT'
MAX_MESSAGE_LINES                 = 1000 # Don't set this too high so that the limits for the logging TextCtrl are not exceeded (whatever the limit may be)
MAIN_WINDOW_WIDTH_INI             = 606
MAIN_WINDOW_HEIGHT_INI            = 500
PLOT_MARKERSIZE                   = 4
PLOT_LINEWIDTH                    = 1.5
GUI_STATICBOX_MARGIN_HOR          = 20  # Horizontal margin space around wx.StaticBoxes
GUI_STATICBOX_MARGIN_VER          = 12  # Vertical margin space around wx.StaticBoxes

DUT_PSU_PARAMETERS                = ('U1',     'I1',     'U2',     'I2')
DUT_PSU_LABELS                    = ('U\u2081','I\u2081','U\u2082','I\u2082')
DUT_PSU_UNITS                     = ('V',      'A',      'V',      'A')
