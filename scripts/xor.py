# coding: utf-8

string = "773063265d3a0e3b0d4d2a1f2e1f2d4f2851377a147620780f214d216c11".decode("hex")

out = ""
for i in range(len(string)-1):
    out += chr(ord(string[i]) ^ ord(string[i+1]))

print out
