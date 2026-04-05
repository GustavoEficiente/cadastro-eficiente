import 'dart:convert';

import 'package:flutter/material.dart';

import '../services/api_service.dart';
import '../services/local_db_service.dart';

class DashboardPage extends StatefulWidget {
  final String username;
  final String nomeExibicao;

  const DashboardPage({
    super.key,
    required this.username,
    required this.nomeExibicao,
  });

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  bool _sincronizando = false;
  String _mensagem = '';

  Future<void> _sincronizarCadastros() async {
    setState(() {
      _sincronizando = true;
      _mensagem = '';
    });

    try {
      final pendentes = await LocalDbService.listarCadastrosPendentes();

      if (pendentes.isEmpty) {
        setState(() {
          _mensagem = 'Nenhum cadastro pendente para sincronizar';
          _sincronizando = false;
        });
        return;
      }

      int sincronizados = 0;

      for (final cadastro in pendentes) {
        Map<String, dynamic> dadosExtras = {};
        List<String> fotos = [];

        final dadosExtrasBruto = cadastro['dados_extras'];
        if (dadosExtrasBruto != null &&
            dadosExtrasBruto.toString().trim().isNotEmpty) {
          try {
            final convertido = jsonDecode(dadosExtrasBruto.toString());
            if (convertido is Map<String, dynamic>) {
              dadosExtras = convertido;
            }
          } catch (_) {}
        }

        final fotosBruto = cadastro['fotos_json'];
        if (fotosBruto != null && fotosBruto.toString().trim().isNotEmpty) {
          try {
            final convertido = jsonDecode(fotosBruto.toString());
            if (convertido is List) {
              fotos = convertido.map((e) => e.toString()).toList();
            }
          } catch (_) {}
        }

        final payload = {
          'id_ponto': cadastro['id_ponto']?.toString() ?? '',
          'nome_cadastrador': cadastro['nome_cadastrador']?.toString() ?? '',
          'data_cadastro': cadastro['data_cadastro']?.toString() ?? '',
          'hora_cadastro': cadastro['hora_cadastro']?.toString() ?? '',
          'latitude': cadastro['latitude']?.toString() ?? '',
          'longitude': cadastro['longitude']?.toString() ?? '',
          'status_sincronizacao': 'sincronizado',
          'dados_extras': dadosExtras,
          'fotos': fotos,
        };

        final response = await ApiService.sincronizarCadastro(payload);

        if (response['ok'] == true) {
          await LocalDbService.marcarComoSincronizado(cadastro['local_id']);
          sincronizados++;
        } else {
          setState(() {
            _mensagem =
                'Falha ao sincronizar.\n${response['mensagem'] ?? ''}\n${response['erro'] ?? ''}\n${response['erros'] ?? ''}';
          });
          _sincronizando = false;
          return;
        }
      }

      setState(() {
        _mensagem = sincronizados > 0
            ? 'Serviço sincronizado com sucesso'
            : 'Nenhum cadastro foi sincronizado';
      });
    } catch (e) {
      setState(() {
        _mensagem = 'Erro ao sincronizar:\n$e';
      });
    } finally {
      if (mounted) {
        setState(() {
          _sincronizando = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final nomeTela =
        widget.nomeExibicao.isNotEmpty ? widget.nomeExibicao : widget.username;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Cadastro Eficiente'),
        backgroundColor: const Color(0xFF0B1F3A),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Olá, $nomeTela',
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _sincronizando ? null : _sincronizarCadastros,
              child: _sincronizando
                  ? const SizedBox(
                      height: 20,
                      width: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Sincronizar'),
            ),
            const SizedBox(height: 16),
            if (_mensagem.isNotEmpty)
              SelectableText(
                _mensagem,
                style: TextStyle(
                  fontSize: 16,
                  color: _mensagem.toLowerCase().contains('sucesso')
                      ? Colors.green
                      : Colors.red,
                  fontWeight: FontWeight.w600,
                ),
              ),
          ],
        ),
      ),
    );
  }
}