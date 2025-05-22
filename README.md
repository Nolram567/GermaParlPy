<h1>GermaParlPy</h1>
<div align="left">
  <a href="https://pypi.org/project/germaparlpy/">
    <img src="https://img.shields.io/pypi/v/germaparlpy.svg" alt="PyPi Latest Release"/>
  </a>
  <a href="https://doi.org/10.5281/zenodo.15180629">
    <img src="https://zenodo.org/badge/DOI/10.5281/zenodo.15180629.svg" alt="DOI">
  </a>
</div>

The GermaParlPy Python package provides functionality to deserialize, serialize, manage, and query the GermaParlTEI[^1]
 corpus and derived corpora.

The GermaParlTEI corpus comprises the plenary protocols of the German Bundestag (parliament), encoded in XML according to the TEI standard. The current version covers the first 19 legislative periods, encompassing transcribed speeches from the Bundestag's constituent session on 7 September 1949 to the final sitting of the Angela Merkel era in 2021. This makes it a valuable resource for research in various scientific disciplines.

For detailed information on the library, visit the [official website](https://nolram567.github.io/GermaParlPy/).

## Use Cases

Potential use cases range from the examination of research questions in political science, history or linguistics to the compilation of training data sets for AI.

In addition, this library makes it possible to access the GermaParl corpus in Python and apply powerful NLP libraries such as spacy or gensim to it. Previously, the corpus could only be accessed using the PolMineR package in the R programming language.

## Installation

GermaParlPy is available on PyPi:

```sh
pip install germaparlpy
```

## API Reference

Click [here](https://nolram567.github.io/GermaParlPy/) for the full API Reference.

## XML Structure

Click [here](https://nolram567.github.io/GermaParlPy/xml-structure.html) to learn more about the XML Structure of the underlying corpus GermaParlTEI[^1].

## Tutorials

I have prepared three example scripts that showcase the utilisation and potential use cases of GermaParlPy. You can find the scripts in the /example directory or [here](https://nolram567.github.io/GermaParlPy/tutorials.html).

## Contributing

Contributions and feedback are welcome! Feel free to write an issue or open a pull request.

## License

The code is licensed under the [MIT License](LICENSE).

The GermaParl corpus, which is not part of this repository, is licensed under a [CLARIN PUB+BY+NC+SA license](https://www.clarin.eu/content/licenses-and-clarin-categories).

## Credits

Developed by [Marlon-Benedikt George](https://github.com/https://github.com/Nolram567).

The underlying data set, the GermaParl corpus, was compiled and released by Blätte & Leonhardt (2024)[^1].
See also their R-Library PolMineR in the context of the [PolMine-Project](https://polmine.github.io/), which served as an inspiration for this library.

[^1]: Blaette, A.and C. Leonhardt. Germaparl corpus of plenary protocols. v2.2.0-rc1, Zenodo, 22 July 2024, doi:10.5281/zenodo.12795193