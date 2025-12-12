from enum import Enum
from xml.sax import ContentHandler, parse
import re
import sys
import codecs
import sqlite3
import pickle
from wordnet import LexicalEntry, Synset, Sense


class SQLLexicon:
    """The Lexicon contains all the synsets and entries"""

    def __init__(self, id, label, language, email, license, version, url, db, cache_size=1000000):
        self.id = id
        self.label = label
        self.language = language
        self.email = email
        self.license = license
        self.version = version
        self.url = url
        self.citation = None
        self.frames = []
        self.comments = {}
        self._dirty_entries = []
        self._dirty_synsets = []
        self._dirty_pseudo_entries = []
        self.cache_size = cache_size
        self.conn = db
        self.conn.execute("""
            PRAGMA foreign_keys = ON;
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id TEXT PRIMARY KEY,
                value BLOB NOT NULL
            )""")
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_entries_id
            ON entries (id)
            """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                member TEXT,
                entry_id TEXT,
                synset_id TEXT,
                pos TEXT
                )""")
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_members_member
            ON members (member)
            """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_members_synset_id
            ON members (synset_id)
            """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS synsets (
                id TEXT PRIMARY KEY,
                value BLOB NOT NULL
            )""")
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_synsets_id
            ON synsets (id)
            """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS senses (
                id TEXT PRIMARY KEY,
                synset_id TEXT,
                entry_id TEXT,
                idx INTEGER
            )""")
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_senses_id
            ON senses (id)
            """)
        self.conn.commit()


    def entries(self):
        self._flush_entries()
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM entries ORDER BY id")
        for row in cursor.fetchall():
            yield pickle.loads(row[0])
        cursor.close()

    def entries_len(self):
        self._flush_entries()
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM entries")
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def pseudo_entries(self):
        self._flush_synsets()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT member, pos, GROUP_CONCAT(synset_id)
            FROM members WHERE entry_id IS NULL 
            GROUP BY member, pos
            """)
        # Get all synset_id with the same members and convert them to
        # LexicalEntry objects
        for row in cursor.fetchall():
            lemma = row[0]
            pos = row[1]
            synset_ids = row[2].split(",")
            entry = LexicalEntry(f"oewn-{escape_lemma(lemma)}-{pos}")
            entry.set_lemma(lemma, pos)
            for idx, synset_id in enumerate(synset_ids):
                sense = Sense(f"{escape_lemma(lemma)}%pseudo:{pos}:{idx+1}",
                              f"oewn-{synset}", None, -1)
                entry.add_sense(sense)
            yield entry
        cursor.close()

    def synsets(self):
        self._flush_synsets()
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM synsets ORDER BY id")
        for row in cursor.fetchall():
            yield pickle.loads(row[0])
        cursor.close()

    def synsets_len(self):
        self._flush_synsets()
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM synsets")
        count = cursor.fetchone()[0]
        cursor.close()
        returncount

    def __str__(self):
        return "Lexicon with ID %s and %d entries and %d synsets" % (
            self.id, entries_len(), synsets_len())

    def _flush_entries(self):
        if len(self._dirty_entries) == 0:
            return
        cursor = self.conn.cursor()
        entries = [(entry.id, pickle.dumps(entry)) for entry in self._dirty_entries]
        cursor.executemany("""
            INSERT INTO entries (id, value)
            VALUES (?, ?)
        """, entries)
        senses = []
        members = []

        for entry in self._dirty_entries:
            for (index, sense) in enumerate(entry.senses):
                senses.append((sense.id, sense.synset, entry.id, index))
                members.append((entry.lemma.written_form, entry.id, sense.synset, entry.lemma.part_of_speech.value))
        cursor.executemany("""
            INSERT INTO senses (id, synset_id, entry_id, idx)
            VALUES (?, ?, ?, ?)
        """, senses)
        cursor.executemany("""
            INSERT INTO members (member, entry_id, synset_id, pos)
            VALUES (?, ?, ?, ?)
        """, members)
        self.conn.commit()
        self._dirty_entries = []
        cursor.close()

    def _flush_synsets(self):
        if len(self._dirty_synsets) == 0:
            return
        cursor = self.conn.cursor()
        cursor.executemany("""
            INSERT INTO synsets (id, value)
            VALUES (?, ?)
        """, [(synset.id, pickle.dumps(synset)) for synset in self._dirty_synsets])
        self.conn.commit()
        self._dirty_synsets = []
        cursor.executemany("""
            INSERT OR IGNORE INTO members (member, synset_id, pos)
            VALUES (?, ?, ?)
        """, self._dirty_pseudo_entries)
        self.conn.commit()
        self._dirty_pseudo_entries = []
        cursor.close()

    def add_entry(self, entry):
        """Add an entry and all its senses"""
        if len(self._dirty_entries) >= self.cache_size:
            self._flush_entries()
        self._dirty_entries.append(entry)

    def del_entry(self, entry):
        """Delete an entry and clear all senses"""
        self._flush_entries()
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM entries
            WHERE id = ?
        """, (entry.id,))
        cursor.execute("""
            DELETE FROM senses
            WHERE entry_id = ?
        """, (entry.id,))
        cursor.execute("""
            DELETE FROM members
            WHERE entry_id = ?
        """, (entry.id,))
        conn.commit()
        cursor.close()

    def del_sense(self, entry, sense):
        """Remove a single sense from an entry"""
        self._flush_entries()
        conn = self.conn
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM senses
            WHERE id = ?
        """, (sense.id,))
        cursor.execute("""
            DELETE FROM members
            WHERE entry_id = ? AND synset_id = ?
        """, (entry.id, sense.synset))
        entry.senses = [s for s in entry.senses if s.id != sense.id]
        cursor.execute("""
            REPLACE INTO entries (id, value)
            VALUES (?, ?)
        """, (entry.id, pickle.dumps(entry)))
        conn.commit()
        cursor.close()

    def add_synset(self, synset):
        """Add a synset"""
        if len(self._dirty_synsets) >= self.cache_size:
            self._flush_synsets()
        self._dirty_synsets.append(synset)

    def entry_by_id(self, id : str) -> LexicalEntry:
        """Get an entry by its ID"""
        self._flush_entries()
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM entries WHERE id = ?", (id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return pickle.loads(row[0])

    def entry_id_by_lemma_synset_id(self, lemma, synset_id):
        """Get an entry ID by its lemma and synset ID"""
        self._flush_entries()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT entry_id FROM members
            WHERE member = ? AND synset_id = ?
        """, (lemma, synset_id))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return row[0]
        else:
            self._dirty_pseudo_entries.append((lemma, synset_id, synset_id[-1]))
    

    def synset_by_id(self, id):
        """Get a synset by its ID"""
        self._flush_synsets()
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM synsets WHERE id = ?", (id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return pickle.loads(row[0])

    def sense_by_id(self, id):
        """Get a sense by its ID"""
        self._flush_entries()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT idx, value FROM senses 
            JOIN entries ON senses.entry_id = entries.id
            WHERE senses.id = ?""", (id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            entry = pickle.loads(row[1])
            index = row[0]
            return entry.senses[index]

    def entry_by_lemma(self, lemma):
        """Get all entry IDs with a given lemma"""
        self._flush_entries()
        cursor = self.conn.cursor()
        cursor.execute("SELECT entry_id FROM members WHERE member = ?", (lemma,))
        rows = cursor.fetchall()
        cursor.close()
        entries = []
        for row in rows:
            entries.append(row[0])
        return entries

    def members_by_id(self, synset_id):
        """Get all members of a synset by its ID"""
        self._flush_entries()
        cursor = self.conn.cursor()
        cursor.execute("SELECT member FROM members WHERE synset_id = ?", (synset_id,))
        rows = cursor.fetchall()
        cursor.close()
        return [row[0] for row in rows]

    def sense_to_synset(self, sense_id):
        """Get the synset ID for a given sense ID"""
        self._flush_entries()
        cursor = self.conn.cursor()
        cursor.execute("SELECT synset_id FROM senses WHERE id = ?", (sense_id,))
        row = cursor.fetchone()
        cursor.close()
        if row:
            return row[0]

    def change_sense_id(self, sense, new_id):
        raise NotImplementedError("Changing sense IDs is not supported in the database-backed Lexicon")

    def to_xml(self, xml_file, part=False):
        xml_file.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
        if part:
            xml_file.write(
                """<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-relaxed-1.3.dtd">\n""")
        else:
            xml_file.write(
                """<!DOCTYPE LexicalResource SYSTEM "http://globalwordnet.github.io/schemas/WN-LMF-1.3.dtd">\n""")
        if self.citation:
            citation_text = f"""
           citation="{self.citation}" """
        else:
            citation_text = ""
        xml_file.write(
            """<LexicalResource xmlns:dc="https://globalwordnet.github.io/schemas/dc/">
  <Lexicon id="%s"
           label="%s"
           language="%s"
           email="%s"
           license="%s"
           version="%s"%s
           url="%s">
""" %
            (self.id,
             self.label,
             self.language,
             self.email,
             self.license,
             self.version,
             citation_text,
             self.url))

        for entry in self.entries():
            entry.to_xml(xml_file, self.comments)
        for entry in self.pseudo_entries():
            entry.to_xml(xml_file, self.comments)
        for synset in self.synsets():
            synset.to_xml(xml_file, self.comments)
        for synbeh in self.frames:
            synbeh.to_xml(xml_file)
        xml_file.write("""  </Lexicon>
</LexicalResource>\n""")
