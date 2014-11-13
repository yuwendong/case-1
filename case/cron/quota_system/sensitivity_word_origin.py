# -*- coding: utf-8 -*-
import json
from config import db
from model import ClassSensitivity, WordSensitivity, PlaceSensitivity ,PersonSensitivity


def set2list(word_set):
    word_list = list(word_set)
    return word_list


def save_sensitivity(topic, start, end):
    class_words_set = set()
    class_words_list = set2list(class_words_set)
    save_class(topic, start, end, class_words_list)
    word_words_set = set()
    word_words_list = set2list(word_words_set)
    save_word(topic, start, end, word_words_list)
    place_words_set = set()
    place_words_list = set2list(place_words_set)
    save_place(topic, start, end, place_words_list)
    person_uid_set = set()
    person_uid_list = set2list(person_uid_set)
    save_person(topic, start, end, person_uid_list)

def save_class(topic, start_ts, end_ts, words_list):
    item = ClassSensitivity(topic, start_ts, end_ts, json.dumps(words_list))
    item_exist = db.session.query(ClassSensitivity).filter(ClassSensitivity.topic==topic ,\
                                                           ClassSensitivity.start_ts==start_ts ,\
                                                           ClassSensitivity.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

def save_word(topic, start_ts, end_ts, words_list):
    item = WordSensitivity(topic, start_ts, end_ts, json.dumps(words_list))
    item_exist = db.session.query(WordSensitivity).filter(WordSensitivity.topic==topic ,\
                                                          WordSensitivity.start_ts==start_ts ,\
                                                          WordSensitivity.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

def save_place(topic, start_ts, end_ts, words_list):
    item = PlaceSensitivity(topic, start_ts, end_ts, json.dumps(words_list))
    item_exist = db.session.query(PlaceSensitivity).filter(PlaceSensitivity.topic==topic ,\
                                                           PlaceSensitivity.start_ts==start_ts ,\
                                                           PlaceSensitivity.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

def save_person(topic, start_ts, end_ts, person_list):
    item = PersonSensitivity(topic, start_ts, end_ts, json.dumps(person_list))
    item_exist = db.session.query(PersonSensitivity).filter(PersonSensitivity.topic==topic ,\
                                                            PersonSensitivity.start_ts==start_ts ,\
                                                            PersonSensitivity.end_ts==end_ts).first()
    if item_exist:
        db.session.delete(item_exist)
    db.session.add(item)

    db.session.commit()

if __name__=='__main__':
    class_words_set = set()
    class_words_list = set2list(class_words_set)
    save_class(topic, start, end, class_words_list)
    word_words_set = set()
    word_words_list = set2list(word_words_set)
    save_word(topic, start, end, word_words_list)
    place_words_set = set()
    place_words_list = set2list(place_words_set)
    save_place(topic, start, end, place_words_list)
    person_uid_set = set()
    person_uid_list = set2list(person_uid_set)
    save_person(topic, start, end, person_uis_list)
