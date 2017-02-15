# gnt-accentuation

putting together existing accentuation code to explain accentuation of each word in GNT

At the moment it's focused on describing the rules around proclitics and enclitics. `analyse_morphgnt.py` will output something like the following (for the entire SBLGNT):

    011037 * | ---- | **- | ---*-- ----- -- | - --* οὐκ οὐ
    011037 * | --*- | --* | ----*- ----- E* | - --* ἔστιν εἰμί
    011037 - | ---- | --* | ------ ----- -- | - --- μου ἐγώ
    
What this is basically saying (in compact form) is:

- οὐκ is not the same as its normalised form
- οὐκ is a proclitic
- οὐκ is an exception to the way ἐστίν is accented
- οὐκ has a movable kappa
- οὐκ is followed by an enclitic
- ἔστιν is not the same as its normalised form
- ἔστιν is preceded by a proclitic
- ἔστιν is an enclitic
- ἔστιν is a variant of ἐστίν
- ἔστιν is preceded by a word that causes it to be accented ἔστιν
- ἔστιν is followed by an enclitic 
- μου is enclitic
    
Lots more coming!
