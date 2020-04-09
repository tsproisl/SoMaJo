#!/usr/bin/env python3

import argparse
import collections
import os


Character = collections.namedtuple("Character", ("char", "token_boundary", "sentence_boundary"))


def arguments():
    """"""
    parser = argparse.ArgumentParser(description="Evaluate tokenization and sentence splitting")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--files", action="store_true", help="SYSTEM and GOLD are files")
    group.add_argument("-d", "--directories", action="store_true", help="SYSTEM and GOLD are directories (filenames have to match)")
    parser.add_argument("--ignore-xml", action="store_true", help="Ignore XML tags for evaluation")
    parser.add_argument("-s", "--sentences", action="store_true", help="Also evaluate sentence boundaries")
    parser.add_argument("-e", "--errors", type=os.path.abspath, help="Write errors to file")
    parser.add_argument("SYSTEM", type=os.path.abspath, help="System output")
    parser.add_argument("GOLD", type=os.path.abspath, help="Gold data")
    args = parser.parse_args()
    return args


def read_characters(f, ignore_xml, sentences):
    characters = []
    for line in f:
        line = line.rstrip()
        if sentences and line == "":
            characters[-1] = Character(characters[-1].char, True, True)
            continue
        if ignore_xml and line.startswith("<") and line.endswith(">"):
            continue
        for char in line:
            characters.append(Character(char, False, False))
        characters[-1] = Character(characters[-1].char, True, False)
    return characters


def char_to_str(system, gold, focus=False):
    """"""
    string = system.char
    if focus:
        # sentence fp
        if system.sentence_boundary and (not gold.sentence_boundary):
            string += "■ "
        # sentence fn
        elif (not system.sentence_boundary) and gold.sentence_boundary:
            string += "□ "
        # token fp
        elif system.token_boundary and (not gold.token_boundary):
            string += "● "
        # token fn
        elif (not system.token_boundary) and gold.token_boundary:
            string += "○ "
        # any tp
        elif (system.sentence_boundary and gold.sentence_boundary) or (system.token_boundary and gold.token_boundary):
            string += " "
    else:
        if system.sentence_boundary or system.token_boundary:
            string += " "
    return string


def precision_recall_f1(tp, fp, fn):
    """"""
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    f1 = (2 * precision * recall) / (precision + recall)
    return precision, recall, f1


def evaluate_file(system_path, gold_path, ignore_xml, sentences, error_file):
    """"""
    print("%s ⇔ %s" % (system_path, gold_path))
    if error_file:
        with open(error_file, mode="a", encoding="utf-8") as e:
            e.write("%s ⇔ %s\n" % (system_path, gold_path))
    with open(system_path, encoding="utf-8") as system, open(gold_path, encoding="utf-8") as gold:
        sys_chars = read_characters(system, ignore_xml, sentences)
        gold_chars = read_characters(gold, ignore_xml, sentences)
        window = collections.deque([""] * 20)
        for s, g in zip(sys_chars, gold_chars):
            window.append(g.char)
            window.popleft()
            if s.char != g.char:
                print("'" + "".join(window) + "'")
                print("'%s' != '%s'" % (s.char, g.char))
                break
        assert len(sys_chars) == len(gold_chars)
        assert all((s.char == g.char for s, g in zip(sys_chars, gold_chars)))
        token_precision, token_recall, token_f1, sentence_precision, sentence_recall, sentence_f1 = 0, 0, 0, 0, 0, 0
        token_tp, token_fp, token_fn, sentence_tp, sentence_fp, sentence_fn = 0, 0, 0, 0, 0, 0
        if error_file:
            with open(error_file, mode="a", encoding="utf-8") as e:
                sys_window = collections.deque([Character("", False, False)] * 41)
                gold_window = collections.deque([Character("", False, False)] * 41)
                for s, g in zip(sys_chars + [Character("", False, False)] * 20, gold_chars + [Character("", False, False)] * 20):
                    sys_window.append(s)
                    sys_window.popleft()
                    gold_window.append(g)
                    gold_window.popleft()
                    if sys_window[20] != gold_window[20]:
                        e.write("%s%s%s\n" % ("".join(char_to_str(x, y) for x, y in zip(list(sys_window)[:20], list(gold_window)[:20]))[-20:],
                                          char_to_str(sys_window[20], gold_window[20], focus=True),
                                          "".join(char_to_str(x, y) for x, y in zip(list(sys_window)[21:], list(gold_window)[21:]))[:20]))
        token_tp = len([s for s, g in zip(sys_chars, gold_chars) if g.token_boundary and s.token_boundary])
        token_fp = len([s for s, g in zip(sys_chars, gold_chars) if (not g.token_boundary) and s.token_boundary])
        token_fn = len([s for s, g in zip(sys_chars, gold_chars) if g.token_boundary and (not s.token_boundary)])
        token_precision, token_recall, token_f1 = precision_recall_f1(token_tp, token_fp, token_fn)
        print("Tokenization:")
        print("P = %6.2f%%   R = %6.2f%%   F = %6.2f%%" % (token_precision * 100, token_recall * 100, token_f1 * 100))
        print("%d false positives, %d false negatives" % (token_fp, token_fn))
        if sentences:
            sentence_tp = len([s for s, g in zip(sys_chars, gold_chars) if g.sentence_boundary and s.sentence_boundary])
            sentence_fp = len([s for s, g in zip(sys_chars, gold_chars) if (not g.sentence_boundary) and s.sentence_boundary])
            sentence_fn = len([s for s, g in zip(sys_chars, gold_chars) if g.sentence_boundary and (not s.sentence_boundary)])
            sentence_precision, sentence_recall, sentence_f1 = precision_recall_f1(sentence_tp, sentence_fp, sentence_fn)
            print("Sentence splitting:")
            print("P = %6.2f%%   R = %6.2f%%   F = %6.2f%%" % (sentence_precision * 100, sentence_recall * 100, sentence_f1 * 100))
            print("%d false positives, %d false negatives" % (sentence_fp, sentence_fn))
        print()
        return token_tp, token_fp, token_fn, token_precision, token_recall, token_f1, sentence_tp, sentence_fp, sentence_fn, sentence_precision, sentence_recall, sentence_f1


def main():
    """"""
    args = arguments()
    if args.errors:
        with open(args.errors, mode="w", encoding="utf-8") as e:
            pass
    if args.files:
        evaluate_file(args.SYSTEM, args.GOLD, args.ignore_xml, args.sentences, args.errors)
    elif args.directories:
        n_tokens, token_precision, token_recall, token_f1, n_sentences, sentence_precision, sentence_recall, sentence_f1 = 0, 0, 0, 0, 0, 0, 0, 0
        token_tp, token_fp, token_fn, sentence_tp, sentence_fp, sentence_fn = 0, 0, 0, 0, 0, 0
        system_files = sorted(os.listdir(args.SYSTEM))
        gold_files = sorted(os.listdir(args.GOLD))
        assert len(system_files) == len(gold_files)
        assert all((s == g for s, g in zip(system_files, gold_files)))
        for system_file, gold_file in zip(system_files, gold_files):
            ttp, tfp, tfn, tp, tr, tf, stp, sfp, sfn, sp, sr, sf = evaluate_file(os.path.join(args.SYSTEM, system_file), os.path.join(args.GOLD, gold_file), args.ignore_xml, args.sentences, args.errors)
            nt = ttp + tfn
            ns = stp + sfp
            token_tp += ttp
            token_fp += tfp
            token_fn += tfn
            sentence_tp += stp
            sentence_fp += sfp
            sentence_fn += sfn
            n_tokens += nt
            token_precision += nt * tp
            token_recall += nt * tr
            token_f1 += nt * tf
            n_sentences += ns
            sentence_precision += ns * sp
            sentence_recall += ns * sr
            sentence_f1 += ns * sf
        print("TOTAL")
        print("Tokenization (weighted average on %d tokens):" % n_tokens)
        print("P = %6.2f%%   R = %6.2f%%   F = %6.2f%%" % (token_precision / n_tokens * 100, token_recall / n_tokens * 100, token_f1 / n_tokens * 100))
        print("%d false positives, %d false negatives" % (token_fp, token_fn))
        if args.sentences:
            print("Sentence splitting (weighted average on %d sentences):" % n_sentences)
            print("P = %6.2f%%   R = %6.2f%%   F = %6.2f%%" % (sentence_precision / n_sentences * 100, sentence_recall / n_sentences * 100, sentence_f1 / n_sentences * 100))
            print("%d false positives, %d false negatives" % (sentence_fp, sentence_fn))


if __name__ == "__main__":
    main()
