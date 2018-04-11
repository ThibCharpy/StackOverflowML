package fr.upmc.stl.dar.projet

import org.apache.spark.{SparkConf, SparkContext}
import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.ml.feature.{HashingTF, IDF, LabeledPoint}
import org.apache.spark.mllib.classification.{NaiveBayes, NaiveBayesModel}

object App {

  val ROOT_PATH: String = "/home/thibault/Documents/FAC/Master/Master_2/DAR/StackOverflowML/"
  val filename: String = "dataset.json"

  def main (arg: Array[String]): Unit = {

    val conf = new SparkConf().setAppName("StackOverflowML").setMaster("local")
    val sc = new SparkContext(conf)
    val sparkSession = SparkSession.builder
      .master("local")
      .appName("StackOverflowML")
      .getOrCreate()

    import sparkSession.sqlContext.implicits._
    val sqlContext = sparkSession.sqlContext

    val dataFrame = sqlContext.read.option("multiline", "true").json("test.json").toDF()
    dataFrame.show()

    val newTextCol = dataFrame.select("text").map(row => cleanStrings(row.getString(0)))
    newTextCol.show()

    /*TF IDF over cleaned datas*/
    val hashingTF = new HashingTF()
    hashingTF.setNumFeatures(10000)
    hashingTF.setInputCol("value")
    hashingTF.setOutputCol("TF")
    val tf: DataFrame = hashingTF.transform(newTextCol.na.drop(Array("value")))
    tf.show()
    tf.cache()
    val idf = new IDF()
    idf.setInputCol("TF")
    idf.setOutputCol("TF-IDF")
    val idf_temp = idf.fit(tf.na.drop(Array("TF")))
    val tfidf: DataFrame = idf_temp.transform(tf)

    tfidf.show()

    /* Préparation des données */

    /* Classfication bayesienne */

  }

  def cleanStrings (string: String): Array[String] = {
    val stopwords_list = Array(
      "a",  "about",  "above",  "after",  "again",  "against",  "all",  "am",  "an",  "and",  "any",  "are",  "arent",  "as",  "at",
     "be",  "because",  "been",  "before",  "being",  "below",  "between",  "both",  "but",  "by",
     "can", "cant", "come",  "could", "couldnt",
     "d",  "did",  "didn",  "do",  "does",  "doesnt",  "doing",  "dont",  "down",  "during",
     "each",
     "few", "finally",  "for",  "from",  "further",
     "had",  "hadnt",  "has",  "hasnt",  "have",  "havent",  "having",  "he",  "her",  "here",  "hers",  "herself",  "him",  "himself",  "his",  "how",
     "i",  "if",  "in",  "into",  "is",  "isnt",  "it",  "its",  "itself",
     "just",
     "ll",
     "m",  "me",  "might",  "more",  "most",  "must",  "my",  "myself",
     "no",  "nor",  "not",  "now",
     "o",  "of",  "off",  "on",  "once",  "only",  "or",  "other",  "our",  "ours",  "ourselves",  "out",  "over",  "own",
     "r",  "re",
     "s", "said",  "same",  "she",  "should",  "shouldnt",  "so",  "some",  "such",
     "t",  "than",  "that", "thats",  "the",  "their",  "theirs",  "them",  "themselves",  "then",  "there",  "these",  "they",  "this",  "those",  "through",  "to",  "too",
     "under",  "until",  "up",
     "very",
     "was",  "wasnt",  "we",  "were",  "werent",  "what",  "when",  "where",  "which",  "while",  "who",  "whom",  "why",  "will",  "with",  "wont",  "would",
     "y",  "yo ",  "your",  "yours",  "yourself",  "yourselves")
    val stopwords_list_custom = Array("")
    val stopwords = stopwords_list ++ stopwords_list_custom

    val words = string.split("[ ]+?")
    var res = words.filter( word => word.matches("[A-Za-z]+"))
    res = res.filter( word => word.toLowerCase.length > 2 && !stopwords.contains(word.toLowerCase()))
    res
  }

}
