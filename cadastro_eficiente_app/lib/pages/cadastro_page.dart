import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';

import '../services/local_db_service.dart';

class CadastroPage extends StatefulWidget {
  final String username;
  final String nomeExibicao;

  const CadastroPage({
    super.key,
    required this.username,
    required this.nomeExibicao,
  });

  @override
  State<CadastroPage> createState() => _CadastroPageState();
}

class _CadastroPageState extends State<CadastroPage> {
  final ImagePicker _picker = ImagePicker();

  final macrorregiaoController = TextEditingController();
  final tipoTecnologiaController = TextEditingController();
  final corpoLuminariaController = TextEditingController();
  final potenciaLuminariaController = TextEditingController();
  final qntLuminariasController = TextEditingController();
  final luminariaAvariadaController = TextEditingController();
  final tipoBracoController = TextEditingController();
  final projecaoBracoController = TextEditingController();
  final bracoAvariadoController = TextEditingController();
  final altLuminariaController = TextEditingController();
  final altPosteController = TextEditingController();
  final materialPosteController = TextEditingController();
  final tipoPosteController = TextEditingController();
  final posteAvariadoController = TextEditingController();
  final redeDistribuicaoController = TextEditingController();
  final posteacaoController = TextEditingController();
  final posteExclusivoIpController = TextEditingController();
  final presencaTransformadorController = TextEditingController();
  final arvoreObstruindoController = TextEditingController();
  final distEntrePostesController = TextEditingController();
  final distPosteMeioFioController = TextEditingController();
  final larguraViaController = TextEditingController();
  final larguraPasseioController = TextEditingController();
  final trocoPontoAmostraController = TextEditingController();

  final latitudeController = TextEditingController();
  final longitudeController = TextEditingController();

  List<XFile?> fotos = List<XFile?>.filled(5, null);

  bool salvando = false;
  String dataAtual = '';
  String horaAtual = '';

  @override
  void initState() {
    super.initState();
    atualizarDataHora();
  }

  void atualizarDataHora() {
    final agora = DateTime.now();
    dataAtual =
        '${agora.year}-${agora.month.toString().padLeft(2, '0')}-${agora.day.toString().padLeft(2, '0')}';
    horaAtual =
        '${agora.hour.toString().padLeft(2, '0')}:${agora.minute.toString().padLeft(2, '0')}:${agora.second.toString().padLeft(2, '0')}';
    setState(() {});
  }

  String gerarIdPonto() {
    final agora = DateTime.now();
    return 'CEF-${agora.year}'
        '${agora.month.toString().padLeft(2, '0')}'
        '${agora.day.toString().padLeft(2, '0')}-'
        '${agora.hour.toString().padLeft(2, '0')}'
        '${agora.minute.toString().padLeft(2, '0')}'
        '${agora.second.toString().padLeft(2, '0')}-'
        '${agora.millisecond.toString().padLeft(3, '0')}';
  }

  Future<void> capturarCoordenadas() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Ative a localização do aparelho.')),
      );
      return;
    }

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }

    if (permission == LocationPermission.deniedForever ||
        permission == LocationPermission.denied) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Permissão de localização negada.')),
      );
      return;
    }

    final pos = await Geolocator.getCurrentPosition();

    latitudeController.text = pos.latitude.toStringAsFixed(7);
    longitudeController.text = pos.longitude.toStringAsFixed(7);
    setState(() {});
  }

  Future<void> tirarFoto(int index) async {
    final foto = await _picker.pickImage(source: ImageSource.camera);
    if (foto != null) {
      fotos[index] = foto;
      setState(() {});
    }
  }

  void limparFormulario() {
    macrorregiaoController.clear();
    tipoTecnologiaController.clear();
    corpoLuminariaController.clear();
    potenciaLuminariaController.clear();
    qntLuminariasController.clear();
    luminariaAvariadaController.clear();
    tipoBracoController.clear();
    projecaoBracoController.clear();
    bracoAvariadoController.clear();
    altLuminariaController.clear();
    altPosteController.clear();
    materialPosteController.clear();
    tipoPosteController.clear();
    posteAvariadoController.clear();
    redeDistribuicaoController.clear();
    posteacaoController.clear();
    posteExclusivoIpController.clear();
    presencaTransformadorController.clear();
    arvoreObstruindoController.clear();
    distEntrePostesController.clear();
    distPosteMeioFioController.clear();
    larguraViaController.clear();
    larguraPasseioController.clear();
    trocoPontoAmostraController.clear();
    latitudeController.clear();
    longitudeController.clear();

    fotos = List<XFile?>.filled(5, null);
    atualizarDataHora();
    setState(() {});
  }

  Future<void> salvarOffline() async {
    setState(() => salvando = true);

    try {
      final fotosPaths = fotos
          .where((f) => f != null)
          .map((f) => f!.path)
          .toList();

      final cadastro = {
        'id_ponto': gerarIdPonto(),
        'username': widget.username,
        'nome_cadastrador': widget.nomeExibicao,
        'data_cadastro': dataAtual,
        'hora_cadastro': horaAtual,
        'latitude': latitudeController.text,
        'longitude': longitudeController.text,
        'tipo_coordenada': 'gps',
        'status_sincronizacao': 'pendente',
        'dados_extras': jsonEncode({
          'macrorregiao': macrorregiaoController.text,
          'tipo_tecnologia': tipoTecnologiaController.text,
          'corpo_luminaria': corpoLuminariaController.text,
          'potencia_luminaria': potenciaLuminariaController.text,
          'qnt_luminarias': qntLuminariasController.text,
          'luminaria_avariada': luminariaAvariadaController.text,
          'tipo_braco': tipoBracoController.text,
          'projecao_braco': projecaoBracoController.text,
          'braco_avariado': bracoAvariadoController.text,
          'alt_luminaria': altLuminariaController.text,
          'alt_poste': altPosteController.text,
          'material_poste': materialPosteController.text,
          'tipo_poste': tipoPosteController.text,
          'poste_avariado': posteAvariadoController.text,
          'rede_distribuicao': redeDistribuicaoController.text,
          'posteacao': posteacaoController.text,
          'poste_exclusivo_ip': posteExclusivoIpController.text,
          'presenca_transformador': presencaTransformadorController.text,
          'arvore_obstruindo': arvoreObstruindoController.text,
          'dist_entre_postes': distEntrePostesController.text,
          'dist_poste_meio_fio': distPosteMeioFioController.text,
          'largura_via': larguraViaController.text,
          'largura_passeio': larguraPasseioController.text,
          'troco_ponto_amostra': trocoPontoAmostraController.text,
        }),
        'fotos_json': jsonEncode(fotosPaths),
      };

      await LocalDbService.salvarCadastro(cadastro);

      limparFormulario();

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cadastro salvo offline com sucesso.')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString())),
      );
    } finally {
      if (mounted) {
        setState(() => salvando = false);
      }
    }
  }

  Widget campoTexto(String label, TextEditingController controller) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextField(
        controller: controller,
        decoration: InputDecoration(labelText: label),
      ),
    );
  }

  Widget cardFoto(int index) {
    final foto = fotos[index];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Text('Foto ${index + 1}'),
            const SizedBox(height: 8),
            SizedBox(
              height: 100,
              width: double.infinity,
              child: foto == null
                  ? const Center(child: Text('Sem foto'))
                  : Image.file(
                      File(foto.path),
                      fit: BoxFit.cover,
                    ),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              onPressed: () => tirarFoto(index),
              child: const Text('Tirar foto'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Card(
            child: ListTile(
              title: const Text('Nome do cadastrador'),
              subtitle: Text(widget.nomeExibicao),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text('Data do cadastro'),
              subtitle: Text(dataAtual),
            ),
          ),
          Card(
            child: ListTile(
              title: const Text('Hora do cadastro'),
              subtitle: Text(horaAtual),
            ),
          ),
          const SizedBox(height: 12),
          campoTexto('Macrorregião', macrorregiaoController),
          campoTexto('Tipo Tecnologia', tipoTecnologiaController),
          campoTexto('Corpo da Luminária', corpoLuminariaController),
          campoTexto('Potência da Luminária', potenciaLuminariaController),
          campoTexto('Qnt. Luminárias', qntLuminariasController),
          campoTexto('Luminária Avariada', luminariaAvariadaController),
          campoTexto('Tipo de Braço', tipoBracoController),
          campoTexto('Projeção do Braço (m)', projecaoBracoController),
          campoTexto('Braço Avariado', bracoAvariadoController),
          campoTexto('Alt. Luminária (m)', altLuminariaController),
          campoTexto('Alt. Poste (m)', altPosteController),
          campoTexto('Material do Poste', materialPosteController),
          campoTexto('Tipo do Poste', tipoPosteController),
          campoTexto('Poste Avariado', posteAvariadoController),
          campoTexto('Rede de Distribuição', redeDistribuicaoController),
          campoTexto('Posteação', posteacaoController),
          campoTexto('Poste Exclusivo de IP', posteExclusivoIpController),
          campoTexto('Presença de Transformador', presencaTransformadorController),
          campoTexto('Árvore Obstruindo', arvoreObstruindoController),
          campoTexto('Dist. entre Postes (m)', distEntrePostesController),
          campoTexto('Dist. Poste Meio Fio (m)', distPosteMeioFioController),
          campoTexto('Largura - Via (m)', larguraViaController),
          campoTexto('Largura - Passeio (m)', larguraPasseioController),
          campoTexto('Troco ponto da amostra', trocoPontoAmostraController),
          TextField(
            controller: latitudeController,
            readOnly: true,
            decoration: const InputDecoration(labelText: 'Latitude'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: longitudeController,
            readOnly: true,
            decoration: const InputDecoration(labelText: 'Longitude'),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: capturarCoordenadas,
              child: const Text('Capturar coordenadas'),
            ),
          ),
          const SizedBox(height: 20),
          const Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Fotos do ponto',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 12),
          cardFoto(0),
          cardFoto(1),
          cardFoto(2),
          cardFoto(3),
          cardFoto(4),
          const SizedBox(height: 20),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: salvando ? null : salvarOffline,
              child: salvando
                  ? const CircularProgressIndicator()
                  : const Text('Salvar cadastro'),
            ),
          ),
        ],
      ),
    );
  }
}