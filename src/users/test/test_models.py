import warnings

from django.core.cache import cache
from django.test import TestCase

from src.users.models import Country, City, User, Lab, UserRating, Type, Service, LabService, Result, Appointment


from newscraper.test.factories_meta import SymbolFactory, ArticleFactory, ArticleCommentFactory, \
    ArticleReactionFactory, CommentReactionFactory, WordcountFactory


@colorize(color=BLUE)
class TestSymbol(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.symbol = SymbolFactory()

    def test_symbol_creation(self):
        symbol_test = self.symbol
        self.assertTrue(isinstance(symbol_test, Symbol))
        """Test Models: Symbol creation -> Working"""

    def test_symbol_default_class(self):
        self.assertEqual(self.symbol.symbol_class, str(Symbol.CLASS_B))
        """Test Models: Symbol class -> Working"""

    def test_symbol_model_name(self):
        symbol_db = Symbol.objects.all()

        print(len(symbol_db))
        """Test Models: Symbol name -> Working"""

    def test_is_enabled_label(self):
        symbol = self.symbol
        field_label = symbol._meta.get_field('is_enabled').verbose_name
        self.assertEqual(field_label, 'is enabled')
        """Test Models: Symbol is enabled -> Working"""

    def test_default_is_enabled_true(self):
        symbol = self.symbol
        is_enabled = symbol._meta.get_field('is_enabled')
        self.assertTrue(is_enabled)
        """Test Models: Symbol is enabled -> Working"""


@colorize(color=BLUE)
class TestArticle(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.article = ArticleFactory()

    def test_default_article(self):
        article = get_default_article()
        self.assertEqual(article.external_id, 'Def123')

    def test_article_creation(self):
        article_test = self.article
        self.assertTrue(isinstance(article_test, Article))
        """Test Models: Article creation -> Working"""

    def test_article_symbol(self):
        self.assertEqual(self.article.symbol.symbol_class, str(Symbol.CLASS_B))
        """Test Models: Article symbol -> Working"""

    def test_article_link(self):
        article_length = len(self.article.article_link)
        self.assertGreater(article_length, 0)
        """Test Models: Article link -> Working"""

    def test_title_label(self):
        article = self.article
        field_label = article._meta.get_field('title').verbose_name
        self.assertEqual(field_label, 'title')
        """Test Models: Article title -> Working"""

    def test_published_at_label(self):
        article = self.article
        field_label = article._meta.get_field('published_at').verbose_name
        self.assertEqual(field_label, 'published at')
        """Test Models: Article published at -> Working"""

    def test_external_id_label(self):
        article = self.article
        field_label = article._meta.get_field('external_id').verbose_name
        self.assertEqual(field_label, 'external id')
        """Test Models: Article external id -> Working"""

    def test_title_max_length(self):
        article = self.article
        max_length = article._meta.get_field('title').max_length
        self.assertEqual(max_length, 250)
        """Test Models: Article title max length -> Working"""

    def test_text_max_length(self):
        article = self.article
        max_length = article._meta.get_field('text').max_length
        self.assertEqual(max_length, 10000)
        """Test Models: Article text max length -> Working"""

    def test_is_archived_label(self):
        article = self.article
        field_label = article._meta.get_field('is_archived').verbose_name
        self.assertEqual(field_label, 'is archived')
        """Test Models: Article is archived -> Working"""

    def test_default_is_archived_false(self):
        article = self.article
        is_archived = article._meta.get_field('is_archived')
        self.assertTrue(is_archived)
        """Test Models: Article is archived -> Working"""

    def test_is_deleted_label(self):
        article = self.article
        field_label = article._meta.get_field('is_deleted').verbose_name
        self.assertEqual(field_label, 'is deleted')
        """Test Models: Article is deleted -> Working"""

    def test_default_is_deleted_false(self):
        article = self.article
        is_deleted = article._meta.get_field('is_deleted')
        self.assertTrue(is_deleted)
        """Test Models: Article is deleted -> Working"""


@colorize(color=BLUE)
class TestComment(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.comment = ArticleCommentFactory()

    def test_default_comment(self):
        comment = get_default_comment()
        self.assertEqual(comment.comment_writer, 'Default')

    def test_article_comment_creation(self):
        comment_test = self.comment
        self.assertTrue(isinstance(comment_test, ArticleComment))
        """Test Models: Comment creation -> Working"""

    def test_comment_text(self):
        comment_length = len(self.comment.text)
        self.assertGreater(comment_length, 0)
        """Test Models: Comment link -> Working"""

    def test_article_commented_label(self):
        comment_test = self.comment
        field_label = comment_test._meta.get_field('article_commented').verbose_name
        self.assertEqual(field_label, 'article commented')
        """Test Models: Article commented -> Working"""

    def test_comment_writer_label(self):
        comment_test = self.comment
        field_label = comment_test._meta.get_field('comment_writer').verbose_name
        self.assertEqual(field_label, 'comment writer')
        """Test Models: Comment writer -> Working"""

    def test_text_label(self):
        comment_test = self.comment
        field_label = comment_test._meta.get_field('text').verbose_name
        self.assertEqual(field_label, 'text')
        """Test Models: Comment text -> Working"""

    def test_commented_at_label(self):
        comment_test = self.comment
        field_label = comment_test._meta.get_field('commented_at').verbose_name
        self.assertEqual(field_label, 'commented at')
        """Test Models: Commented at -> Working"""

    def test_updated_at_label(self):
        comment_test = self.comment
        field_label = comment_test._meta.get_field('updated_at').verbose_name
        self.assertEqual(field_label, 'updated at')
        """Test Models: Updated at -> Working"""

    def test_is_deleted_label(self):
        comment_test = self.comment
        field_label = comment_test._meta.get_field('is_deleted').verbose_name
        self.assertEqual(field_label, 'is deleted')
        """Test Models: Comment is deleted -> Working"""

    def test_default_is_deleted_false(self):
        comment_test = self.comment
        is_deleted = comment_test._meta.get_field('is_deleted')
        self.assertTrue(is_deleted)
        """Test Models: Comment is deleted -> Working"""


@colorize(color=BLUE)
class TestWordcount(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.wordcount = WordcountFactory()

    def test_wordcount_creation(self):
        wordcount_test = self.wordcount
        self.assertTrue(isinstance(wordcount_test, Wordcount))
        """Test Models: Wordcount creation -> Working"""

    def test_wordcount_model_word(self):
        wordcount_db = Wordcount.objects.all()

        print(len(wordcount_db))
        """Test Models: Wordcount word -> Working"""

    def test_count_label(self):
        wordcount_test = self.wordcount
        field_label = wordcount_test._meta.get_field('count').verbose_name
        self.assertEqual(field_label, 'count')
        """Test Models: Wordcount count -> Working"""

    def test_updated_at_label(self):
        wordcount_test = self.wordcount
        field_label = wordcount_test._meta.get_field('updated_at').verbose_name
        self.assertEqual(field_label, 'updated at')
        """Test Models: Wordcount updated at -> Working"""


@colorize(color=BLUE)
class TestArticleReaction(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.reaction = ArticleReactionFactory()

    def test_reaction_creation(self):
        reaction_test = self.reaction
        self.assertTrue(isinstance(reaction_test, ArticleReaction))
        """Test Models: Article reaction creation -> Working"""

    def test_article_label(self):
        reaction_test = self.reaction
        field_label = reaction_test._meta.get_field('article').verbose_name
        self.assertEqual(field_label, 'article')
        """Test Models: Article reaction article -> Working"""

    def test_reacted_at_label(self):
        reaction_test = self.reaction
        field_label = reaction_test._meta.get_field('reacted_at').verbose_name
        self.assertEqual(field_label, 'reacted at')
        """Test Models: Article reaction created at -> Working"""

    def test_reaction_label(self):
        reaction_test = self.reaction
        field_label = reaction_test._meta.get_field('reaction').verbose_name
        self.assertEqual(field_label, 'reaction')
        """Test Models: Article reaction label -> Working"""


@colorize(color=BLUE)
class TestCommentReaction(TestCase):

    def setUp(self):
        warnings.simplefilter('ignore', category=ImportWarning)
        self.reaction = CommentReactionFactory()

    def test_reaction_creation(self):
        reaction_test = self.reaction
        self.assertTrue(isinstance(reaction_test, CommentReaction))
        """Test Models: Comment reaction creation -> Working"""

    def test_comment_label(self):
        reaction_test = self.reaction
        field_label = reaction_test._meta.get_field('comment').verbose_name
        self.assertEqual(field_label, 'comment')
        """Test Models: Comment reaction comment -> Working"""

    def test_reacted_at_label(self):
        reaction_test = self.reaction
        field_label = reaction_test._meta.get_field('reacted_at').verbose_name
        self.assertEqual(field_label, 'reacted at')
        """Test Models: Comment reaction created at -> Working"""

    def test_reaction_label(self):
        reaction_test = self.reaction
        field_label = reaction_test._meta.get_field('reaction').verbose_name
        self.assertEqual(field_label, 'reaction')
        """Test Models: Comment reaction label -> Working"""