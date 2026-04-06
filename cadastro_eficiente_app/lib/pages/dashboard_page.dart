import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/api_service.dart';
import 'login_page.dart';

class DashboardPage extends StatefulWidget {
  final String? username;
  final String? nomeExibicao;

  const DashboardPage({
    super.key,
    this.username,
    this.nomeExibicao,
  });

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  String baseUrl = '';
  String username = '';
  String nomeExibicao = '';
  bool carregando = false;
  File? fotoSelecionada;

  @override
  void initState() {
    super.initState();
    carregarSessao();
  }

  Future<void> carregarSessao() async {
    final prefs = await SharedPreferences.getInstance();

    setState(() {
      baseUrl = prefs.getString('base_url') ??
          'https://cadastro-eficiente-1.onrender.com';

      username = widget.username ??
          prefs.getString('username') ??
          '';

      nomeExibicao = widget.nomeExibicao ??
          prefs.getString('nome_exibicao') ??
          username;
    });
  }

  Future<void> selecionarFoto() async {
    try {
      final picker = ImagePicker();

      final XFile? imagem = await picker.pickImage(
        source: ImageSource.gallery,
        imageQuality: 85,
      );

      if (imagem == null) return;

      setState(() {
        fotoSelecionada = File(imagem.path);
      });

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Foto selecionada: ${imagem.path}')),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao selecionar foto: $e')),
      );
    }
  }

  String gerarIdPonto() {
    final agora = DateTime.now();
    final data =
        '${agora.year.toString().padLeft(4, '0')}${agora.month.toString().padLeft(2, '0')}${agora.day.toString().padLeft(2, '0')}';
    final hora =
        '${agora.hour.toString().padLeft(2, '0')}${agora.minute.toString().padLeft(2, '0')}${agora.second.toString().padLeft(2, '0')}';
    return 'CEF-$data-$hora';
  }

  Future<void> sincronizarTeste() async {
    if (baseUrl.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Base URL não encontrada')),
      );
      return;
    }

    if (fotoSelecionada == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Selecione uma foto antes de enviar')),
      );
      return;
    }

    setState(() => carregando = true);

    try {
      final agora = DateTime.now();

      final payload = {
        'id_ponto': gerarIdPonto(),
        'nome_cadastrador': nomeExibicao.isEmpty ? 'TESTE1' : nomeExibicao,
        'data_cadastro':
            '${agora.year.toString().padLeft(4, '0')}-${agora.month.toString().padLeft(2, '0')}-${agora.day.toString().padLeft(2, '0')}',
        'hora_cadastro':
            '${agora.hour.toString().padLeft(2, '0')}:${agora.minute.toString().padLeft(2, '0')}:${agora.second.toString().padLeft(2, '0')}',
        'latitude': '-3.8008650',
        'longitude': '-38.5192489',
        'status_sincronizacao': 'Sincronizado',
        'dados_extras': {
          'origem': 'flutter_app',
          'usuario_login': username,
          'nome_exibicao': nomeExibicao,
          'foto_path': fotoSelecionada!.path,
        },
      };

      final response = await ApiService.sincronizarCadastro(
        payload,
        baseUrl: baseUrl,
        fotoPath: fotoSelecionada!.path,
      );

      if ((response['success'] == true) || (response['ok'] == true)) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Cadastro enviado com sucesso. ID ponto: ${response['id_ponto'] ?? ''}',
            ),
          ),
        );

        setState(() {
          fotoSelecionada = null;
        });
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              response['message']?.toString() ??
                  response['mensagem']?.toString() ??
                  'Erro ao sincronizar',
            ),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao sincronizar: $e')),
      );
    } finally {
      if (mounted) {
        setState(() => carregando = false);
      }
    }
  }

  Future<void> sair() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('username');
    await prefs.remove('nome_exibicao');

    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginPage()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final nomeArquivo =
        fotoSelecionada?.path.split(Platform.pathSeparator).last;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        centerTitle: true,
        actions: [
          IconButton(
            onPressed: sair,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: ListView(
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Servidor: $baseUrl'),
                      const SizedBox(height: 8),
                      Text('Usuário: $username'),
                      const SizedBox(height: 8),
                      Text('Nome: $nomeExibicao'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: selecionarFoto,
                icon: const Icon(Icons.photo),
                label: const Text('Selecionar foto'),
              ),
              const SizedBox(height: 12),
              if (fotoSelecionada != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Foto selecionada: $nomeArquivo'),
                    const SizedBox(height: 8),
                    Text('Caminho: ${fotoSelecionada!.path}'),
                    const SizedBox(height: 12),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(12),
                      child: Image.file(
                        fotoSelecionada!,
                        height: 220,
                        fit: BoxFit.cover,
                      ),
                    ),
                  ],
                )
              else
                const Text('Nenhuma foto selecionada.'),
              const SizedBox(height: 24),
              SizedBox(
                height: 52,
                child: ElevatedButton(
                  onPressed: carregando ? null : sincronizarTeste,
                  child: carregando
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Text('Enviar cadastro com foto'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}